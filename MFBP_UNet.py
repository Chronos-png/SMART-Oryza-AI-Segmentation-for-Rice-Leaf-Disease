import torch
import torch.nn as nn
import torch.nn.functional as F
import math

# ---------------------------
# Basic blocks
# ---------------------------
class ConvBNReLU(nn.Module):
    def __init__(self, in_ch, out_ch, kernel=3, stride=1, padding=None, dilation=1):
        super().__init__()
        if padding is None:
            padding = (kernel - 1) // 2 * dilation
        self.conv = nn.Conv2d(in_ch, out_ch, kernel, stride, padding, dilation=dilation, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)
        self.act = nn.ReLU(inplace=True)
    def forward(self,x):
        return self.act(self.bn(self.conv(x)))

class DWConv(nn.Module):
    def __init__(self, channels, kernel):
        super().__init__()
        padding = (kernel-1)//2
        self.dw = nn.Conv2d(channels, channels, kernel, padding=padding, groups=channels, bias=False)
        self.pw = nn.Conv2d(channels, channels, 1, bias=False)
        self.bn = nn.BatchNorm2d(channels)
        self.act = nn.ReLU(inplace=True)
    def forward(self,x):
        return self.act(self.bn(self.pw(self.dw(x))))

# ---------------------------
# MFE module
# ---------------------------
class MFE(nn.Module):
    """
    Multi-scale Feature Extraction module:
    - base 3x3 conv -> branch 3x3 dilated (detail) & 5x5 (semantic)
    - concat -> 1x1 compress -> depthwise convs with kernels 3,5,7 (sum) -> pw conv
    - frequency attention: use fft2 magnitude pooled across spatial dims -> fc -> sigmoid
    """
    def __init__(self, in_ch, out_ch, groups=1):
        super().__init__()
        mid = max(1, out_ch // 2)
        self.base = ConvBNReLU(in_ch, mid, kernel=3)
        # branches
        self.branch_d = ConvBNReLU(mid, mid, kernel=3, dilation=2)   # detail (dilated)
        self.branch_c = ConvBNReLU(mid, mid, kernel=5)               # coarse/semantic
        self.compress = nn.Conv2d(mid*2, out_ch, 1, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)
        # depthwise branches
        self.dw3 = nn.Conv2d(out_ch, out_ch, 3, padding=1, groups=out_ch, bias=False)
        self.dw5 = nn.Conv2d(out_ch, out_ch, 5, padding=2, groups=out_ch, bias=False)
        self.dw7 = nn.Conv2d(out_ch, out_ch, 7, padding=3, groups=out_ch, bias=False)
        self.pw = nn.Conv2d(out_ch, out_ch, 1, bias=False)
        self.act = nn.ReLU(inplace=True)
        # freq attention: ensure hidden > 0
        hidden = max(1, out_ch // 4)
        self.fc = nn.Sequential(
            nn.Linear(out_ch, hidden),
            nn.ReLU(inplace=True),
            nn.Linear(hidden, out_ch),
            nn.Sigmoid()
        )
        # residual
        if in_ch != out_ch:
            self.res_conv = nn.Conv2d(in_ch, out_ch, 1, bias=False)
        else:
            self.res_conv = None

    def forward(self, x):
        b,c,h,w = x.shape
        base = self.base(x)
        d = self.branch_d(base)
        cse = self.branch_c(base)
        cat = torch.cat([d, cse], dim=1)
        comp = self.compress(cat)
        comp = self.bn(comp)
        # depthwise multi-kernels (sum)
        dw = self.dw3(comp) + self.dw5(comp) + self.dw7(comp)
        dw = self.pw(dw)
        dw = self.act(dw)
        # frequency attention: use fft magnitude pooled per-channel
        fft = torch.fft.fft2(dw, norm='ortho')   # complex tensor
        mag = torch.abs(fft)                     # real-valued magnitude
        mag_pool = mag.mean(dim=(-2,-1))         # shape (B, C)
        att = self.fc(mag_pool)                  # (B, C)
        att = att.unsqueeze(-1).unsqueeze(-1)    # (B, C, 1, 1)
        res = self.res_conv(x) if self.res_conv else x
        out = dw * att + res
        return out

# ---------------------------
# BATok-MLP module (approx)
# ---------------------------
class PatchEmbedding(nn.Module):
    def __init__(self, in_ch, embed_dim):
        super().__init__()
        self.proj = nn.Conv2d(in_ch, embed_dim, kernel_size=3, padding=1, bias=False)
        self.ln = nn.LayerNorm(embed_dim)
    def forward(self, x):
        # x: B,C,H,W -> B,embed_dim,H,W -> flatten N=H*W -> B,N,embed_dim
        y = self.proj(x)
        b,e,h,w = y.shape
        y_flat = y.flatten(2).transpose(1,2)  # B, N, E
        y_flat = self.ln(y_flat)
        return y_flat, (h,w)

def topk_gather(tensor, idx):
    """
    tensor: B, N, C
    idx: B, N, k  (for each of N "queries" we have k neighbor indices)
    returns: B, N, k, C
    Implementation uses python loop over batch (ok for small B).
    """
    b,n,c = tensor.shape
    _, _, k = idx.shape
    out = []
    for i in range(b):
        # idx[i] shape: N, k  -> indexing tensor[i] yields (N, k, C)
        out.append(tensor[i][idx[i]])  # -> N,k,C
    out = torch.stack(out, dim=0)      # B,N,k,C
    return out

class DynamicSparseAttention(nn.Module):
    def __init__(self, region_k=4):
        super().__init__()
        self.region_k = region_k

    def forward(self, Q, K, V, S=None):
        # Q,K,V: B, N, C
        b,n,c = Q.shape
        # compute pairwise adjacency (dot product) between regions
        # Xr: B, n, n where Xr[b,i,j] = dot(Q[b,i], K[b,j])
        Xr = torch.matmul(Q, K.transpose(1,2))  # B, n, n
        # top-k per row:
        k = min(self.region_k, n)
        _, idx = torch.topk(Xr, k=k, dim=-1)  # B, n, k
        # gather corresponding K and V for each region
        Kg = topk_gather(K, idx)  # B, n, k, C
        Vg = topk_gather(V, idx)  # B, n, k, C
        # Now compute attention: for each region i, compute attention between Q[i] and Kg[i]
        Q_exp = Q.unsqueeze(2).expand(-1,-1,k,-1)  # B,n,k,C
        scores = (Q_exp * Kg).sum(-1) / math.sqrt(c)  # B,n,k
        attw = F.softmax(scores, dim=-1).unsqueeze(-1)  # B,n,k,1
        out = (attw * Vg).sum(2)  # B,n,C
        return out

class ShiftedMLP(nn.Module):
    def __init__(self, dim, hidden_dim):
        super().__init__()
        self.fc1 = nn.Linear(dim, hidden_dim)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden_dim, dim)
    def forward(self, x):
        # x: B, N, C
        return self.fc2(self.act(self.fc1(x)))

class TokMLPBlock(nn.Module):
    def __init__(self, embed_dim, hidden_dim):
        super().__init__()
        # shift function not strictly necessary here but kept for conceptual parity
        self.token_conv = nn.Conv1d(embed_dim, embed_dim, kernel_size=3, padding=1, groups=1, bias=False)
        self.mlp = ShiftedMLP(embed_dim, hidden_dim)
        self.dwconv = nn.Conv1d(embed_dim, embed_dim, kernel_size=3, padding=1, groups=embed_dim, bias=False)
        self.ln = nn.LayerNorm(embed_dim)
    def forward(self, x, H, W):
        # x: B, N, C where N = H*W
        b,n,c = x.shape
        # simple token shift via roll (approx)
        x_shift = torch.roll(x, shifts=1, dims=1)
        # token conv expects (B,C,N)
        t = x_shift.transpose(1,2)
        t = self.token_conv(t)
        t = t.transpose(1,2)
        y = self.mlp(t)
        # depthwise conv across tokens
        dw = self.dwconv(y.transpose(1,2)).transpose(1,2)
        out = self.ln((y + dw))
        return out

class BATokMLP(nn.Module):
    def __init__(self, in_ch, embed_dim=128, region_k=4, hidden_dim=256):
        super().__init__()
        self.patch_embed = PatchEmbedding(in_ch, embed_dim)
        self.qkv_proj = nn.Linear(embed_dim, embed_dim*3)
        self.region_k = region_k
        self.att = DynamicSparseAttention(region_k=region_k)
        self.tokblock = TokMLPBlock(embed_dim, hidden_dim)
        self.out_proj = nn.Linear(embed_dim, in_ch)  # project back to channel space

    def forward(self, x):
        # x: B,C,H,W
        b,c,h,w = x.shape
        x_flat, (H,W) = self.patch_embed(x)  # B, N, E
        N = x_flat.shape[1]
        qkv = self.qkv_proj(x_flat)  # B,N,3E
        Q, K, V = torch.chunk(qkv, 3, dim=-1)
        # dynamic sparse attention
        att_out = self.att(Q, K, V, S=None)  # returns B,N,E
        # Tok-MLP (shifted MLP + DW conv)
        tok_out = self.tokblock(att_out, H, W)  # B,N,E
        # project back to 2D feature map
        proj = self.out_proj(tok_out)  # B,N,C_out(where C_out=in_ch)
        proj2d = proj.transpose(1,2).view(b, c, H, W)
        return proj2d

# ---------------------------
# UNet backbone with modules
# ---------------------------
class DownBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv1 = ConvBNReLU(in_ch, out_ch)
        self.conv2 = ConvBNReLU(out_ch, out_ch)
        self.mfe = MFE(out_ch, out_ch)
        self.pool = nn.MaxPool2d(2)
    def forward(self,x):
        y = self.conv1(x)
        y = self.conv2(y)
        y = self.mfe(y)
        p = self.pool(y)
        return y, p

class UpBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.up = nn.ConvTranspose2d(in_ch, out_ch, kernel_size=2, stride=2)
        # note: after concatenation channels become out_ch + skip_ch; in_ch here equals (out_ch + skip_ch)
        self.conv1 = ConvBNReLU(in_ch, out_ch, kernel=3)
        self.conv2 = ConvBNReLU(out_ch, out_ch, kernel=3)
    def forward(self, x, skip):
        x = self.up(x)
        # pad/resize if necessary
        if x.shape[2:] != skip.shape[2:]:
            x = F.interpolate(x, size=skip.shape[2:], mode='bilinear', align_corners=False)
        x = torch.cat([x, skip], dim=1)
        x = self.conv1(x)
        x = self.conv2(x)
        return x

class MFBP_UNet(nn.Module):
    def __init__(self, in_ch=3, num_classes=2, base_ch=32):
        super().__init__()
        # encoder
        self.enc1 = DownBlock(in_ch, base_ch)           # 512 -> 256
        self.enc2 = DownBlock(base_ch, base_ch*2)       # 256 -> 128
        self.enc3 = DownBlock(base_ch*2, base_ch*4)     # 128 -> 64
        self.enc4 = DownBlock(base_ch*4, base_ch*8)     # 64 -> 32
        # bottleneck
        self.bottleneck_conv = nn.Sequential(
            ConvBNReLU(base_ch*8, base_ch*16),
            ConvBNReLU(base_ch*16, base_ch*16)
        )
        # BATok-MLP inserted at end of encoder (as in paper)
        self.batok = BATokMLP(base_ch*16, embed_dim=base_ch*8, region_k=6, hidden_dim=base_ch*32)
        # decoder
        self.up4 = UpBlock(base_ch*16, base_ch*8)
        self.up3 = UpBlock(base_ch*8, base_ch*4)
        self.up2 = UpBlock(base_ch*4, base_ch*2)
        self.up1 = UpBlock(base_ch*2, base_ch)
        # final
        self.final = nn.Conv2d(base_ch, num_classes, kernel_size=1)

    def forward(self, x):
        s1, p1 = self.enc1(x)
        s2, p2 = self.enc2(p1)
        s3, p3 = self.enc3(p2)
        s4, p4 = self.enc4(p3)
        b = self.bottleneck_conv(p4)
        # apply batok (global fusion)
        b = self.batok(b)
        d4 = self.up4(b, s4)
        d3 = self.up3(d4, s3)
        d2 = self.up2(d3, s2)
        d1 = self.up1(d2, s1)
        out = self.final(d1)
        return out
