import torch


def GetMean_SD(feature, delt=1e-5):
    f_size = feature.size()
    assert (len(f_size)==4)
    n, c = f_size[:2]
    miu = feature.view(n, c, -1).mean(dim=2).view(n, c, 1, 1)

    var = feature.view(n, c, -1).var(dim=2)+delt   # + small things
    sd = var.sqrt().view(n, c, 1, 1)
    return miu, sd

def GainFlatFeats_MiuSD(feature): #flatten
    assert (feature.size()[0] == 3)
    assert (isinstance(feature, torch.FloatTensor))
    flattened_feat = feature.view(3, -1)

    sd = flattened_feat.std(dim=-1, keepdim=True)
    miu = flattened_feat.mean(dim=-1, keepdim=True)

    return flattened_feat, miu, sd


def inv_sqaure(x):
    U, X, V = torch.svd(x)
    return torch.mm(torch.mm(U, X.pow(0.5).diag()), V.t())


def adain_layer(StyleFeat, ContentFeat):
    assert (StyleFeat.size()[:2]==ContentFeat.size()[:2])
    sz = ContentFeat.size()

    content_miu, content_SD = GetMean_SD(ContentFeat)
    style_miu, style_SD = GetMean_SD(StyleFeat)

    centralize_feat = (ContentFeat-content_miu.expand(sz)) / content_SD.expand(sz)
    return style_miu.expand(sz) + style_SD.expand(sz)*centralize_feat


def color_prev(origin, destination):

    destination_flat, destination_f_miu, destination_f_sd = GainFlatFeats_MiuSD(destination)
    destination_flat_norm = (destination_flat - destination_f_miu.expand_as(
                                destination_flat)) / destination_f_sd.expand_as(destination_flat)
    destination_flat_cov_eye = torch.eye(3) + torch.mm(destination_flat_norm, destination_flat_norm.t())

    origin_flat, origin_f_miu, origin_f_sd = GainFlatFeats_MiuSD(origin)
    origin_flat_norm = (origin_flat-origin_f_miu.expand_as(origin_flat)) / origin_f_sd.expand_as(origin_flat)
    origin_flat_cov_eye = torch.eye(3) + torch.mm(origin_flat_norm, origin_flat_norm.t())

    origin_flat_norm_transfer = torch.mm( inv_sqaure(destination_flat_cov_eye),
        torch.mm(torch.inverse(inv_sqaure(origin_flat_cov_eye)),  origin_flat_norm) )

    origin_flat_transfer = destination_f_miu.expand_as(origin_flat_norm) + \
                        origin_flat_norm_transfer*destination_f_sd.expand_as(origin_flat_norm)

    return origin_flat_transfer.view(origin.size())
