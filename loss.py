import torch
import numpy as np
import cv2
import torch.nn.functional as F

def get_cc_metric(preds,labels):
    return cc(preds,labels).item()

def get_kl_metric(preds,labels):
    return kldiv(preds,labels).item()

def get_sim_metric(preds,labels):
    return similarity(preds,labels).item()

def get_nss_metric(preds,fixs):
    return nss(preds,fixs).item()
def get_dice_metric(preds,labels):
    return dice_c(preds,labels).item()
#
# def dice_c(y_pred,y_true, smooth=1e-6):
#     """
#     计算适用于概率标签的Dice系数
#     y_true: 真值标签 (numpy array, 值在[0, 1]之间)
#     y_pred: 预测概率 (numpy array, 值在[0, 1]之间)
#     smooth: 防止除零的平滑因子
#     """
#     # y_pred1=y_pred.squeeze()
#     # bce_loss_function = nn.BCELoss()
#     threshold = 0.5  # 设定阈值
#     threshold1 = 0.1 # 设定阈值
#     y_pred = (y_pred > threshold).float()
#     y_true = (y_true > threshold1).float()
#     intersection = (y_true * y_pred).sum()
#     union = (y_true).sum() + (y_pred).sum()
#     dice = (2. * intersection + smooth) / (union + smooth)
#     # return dice+bce_loss_function(y_pred1,y_true)
#     return dice
def dice_c(logits,target, smooth=1e-6):
    """
    计算适用于概率标签的Dice系数
    y_true: 真值标签 (numpy array, 值在[0, 1]之间)
    y_pred: 预测概率 (numpy array, 值在[0, 1]之间)
    smooth: 防止除零的平滑因子
    """
    # threshold = 0.5  # 设定阈值
    # threshold1 = 0.01  # 设定阈值
    # logits = (logits > threshold).float()
    # target = (targets > threshold1).float()
    logits = logits.squeeze(1)  # 将输入的形状从 (4, 1, 352, 352) 改为 (4, 352, 352)

    # target = targets.float()
    # smooth = 1.0
    intersect = torch.sum(logits * target)
    y_sum = torch.sum(target * target)
    z_sum = torch.sum(logits * logits)
    dice = (2 * intersect + smooth) / (z_sum + y_sum + smooth)
    # return dice+bce_loss_function(y_pred1,y_true)
    return dice


def kldiv(s_map, gt):
    batch_size = s_map.size(0)
    w = s_map.size(1)
    h = s_map.size(2)

    sum_s_map = torch.sum(s_map.view(batch_size, -1), 1)
    expand_s_map = sum_s_map.view(batch_size, 1, 1).expand(batch_size, w, h)
    # print(expand_s_map.shape)
    # print(s_map.shape)
    assert expand_s_map.size() == s_map.size()

    sum_gt = torch.sum(gt.view(batch_size, -1), 1)
    expand_gt = sum_gt.view(batch_size, 1, 1).expand(batch_size, w, h)
    # print(expand_gt.shape)
    # print(gt.shape)
    # print(expand_gt.size(),gt.size())
    assert expand_gt.size() == gt.size()

    s_map = s_map / (expand_s_map * 1.0)
    gt = gt / (expand_gt * 1.0)

    s_map = s_map.view(batch_size, -1)
    gt = gt.view(batch_size, -1)

    eps = 2.2204e-16
    result = gt * torch.log(eps + gt / (s_map + eps))

    return torch.mean(torch.sum(result, 1))


def normalize_map(s_map):
    # normalize the salience map (as done in MIT code)
    batch_size = s_map.size(0)
    w = s_map.size(1)
    h = s_map.size(2)

    min_s_map = torch.min(s_map.view(batch_size, -1), 1)[0].view(batch_size, 1, 1).expand(batch_size, w, h)
    max_s_map = torch.max(s_map.view(batch_size, -1), 1)[0].view(batch_size, 1, 1).expand(batch_size, w, h)

    norm_s_map = (s_map - min_s_map) / (max_s_map - min_s_map * 1.0)
    return norm_s_map


def similarity(s_map, gt):
    ''' For single image metric
        Size of Image - WxH or 1xWxH
        gt is ground truth saliency map
    '''
    batch_size = s_map.size(0)
    w = s_map.size(1)
    h = s_map.size(2)

    s_map = normalize_map(s_map)
    gt = normalize_map(gt)

    sum_s_map = torch.sum(s_map.view(batch_size, -1), 1)
    expand_s_map = sum_s_map.view(batch_size, 1, 1).expand(batch_size, w, h)

    assert expand_s_map.size() == s_map.size()

    sum_gt = torch.sum(gt.view(batch_size, -1), 1)
    expand_gt = sum_gt.view(batch_size, 1, 1).expand(batch_size, w, h)

    s_map = s_map / (expand_s_map * 1.0)
    gt = gt / (expand_gt * 1.0)

    s_map = s_map.view(batch_size, -1)
    gt = gt.view(batch_size, -1)
    return torch.mean((torch.sum(torch.min(s_map, gt)+1e-8, 1)))




# def cc(s_map, gt):
#     batch_size = s_map.size(0)
#     w = s_map.size(1)
#     h = s_map.size(2)
#
#     mean_s_map = torch.mean(s_map.view(batch_size, -1), 1).view(batch_size, 1, 1).expand(batch_size, w, h)
#     std_s_map = torch.std(s_map.view(batch_size, -1), 1).view(batch_size, 1, 1).expand(batch_size, w, h)
#
#     mean_gt = torch.mean(gt.view(batch_size, -1), 1).view(batch_size, 1, 1).expand(batch_size, w, h)
#     std_gt = torch.std(gt.view(batch_size, -1), 1).view(batch_size, 1, 1).expand(batch_size, w, h)
#
#     s_map = (s_map - mean_s_map) / std_s_map
#     gt = (gt - mean_gt) / std_gt
#
#     ab = torch.sum((s_map * gt).view(batch_size, -1), 1)
#     aa = torch.sum((s_map * s_map).view(batch_size, -1), 1)
#     bb = torch.sum((gt * gt).view(batch_size, -1), 1)
#
#     return  torch.mean((ab / (torch.sqrt(aa * bb +1e-4))) )
def cc(s_map, gt):
    batch_size = s_map.size(0)

    # 保持原始标准化逻辑
    mean_s_map = torch.mean(s_map.view(batch_size, -1), 1)
    std_s_map = torch.std(s_map.view(batch_size, -1), 1)

    mean_gt = torch.mean(gt.view(batch_size, -1), 1)
    std_gt = torch.std(gt.view(batch_size, -1), 1)

    # 保持原始广播方式
    s_map_norm = (s_map - mean_s_map.view(batch_size, 1, 1)) / (std_s_map.view(batch_size, 1, 1) + 1e-8)
    gt_norm = (gt - mean_gt.view(batch_size, 1, 1)) / (std_gt.view(batch_size, 1, 1) + 1e-8)

    # 保持原始计算方式
    ab = torch.sum((s_map_norm * gt_norm).view(batch_size, -1), 1)
    aa = torch.sum((s_map_norm ** 2).view(batch_size, -1), 1)
    bb = torch.sum((gt_norm ** 2).view(batch_size, -1), 1)

    # 仅增强分母稳定性
    denominator = torch.sqrt(aa * bb + 1e-8)  # 保持原始epsilon值

    return torch.mean(ab / denominator)


def nss(s_map, gt):

    assert s_map.size() == gt.size()
    batch_size = s_map.size(0)
    w = s_map.size(1)
    h = s_map.size(2)
    mean_s_map = torch.mean(s_map.view(batch_size, -1), 1).view(batch_size, 1, 1).expand(batch_size, w, h)
    std_s_map = torch.std(s_map.view(batch_size, -1), 1).view(batch_size, 1, 1).expand(batch_size, w, h)

    eps = 1e-6
    s_map = (s_map - mean_s_map) / (std_s_map + eps)

    s_map = torch.sum((s_map * gt).view(batch_size, -1), 1)
    count = torch.sum(gt.view(batch_size, -1), 1)
    return torch.mean(s_map / count)



def auc_judd(saliencyMap, fixationMap, jitter=True, toPlot=False, normalize=False):
    # saliencyMap is the saliency map
    # fixationMap is the human fixation map (binary matrix)
    # jitter=True will add tiny non-zero random constant to all map locations to ensure
    #       ROC can be calculated robustly (to avoid uniform region)
    # if toPlot=True, displays ROC curve

    # If there are no fixations to predict, return NaN
    if saliencyMap.size() != fixationMap.size():
        saliencyMap = saliencyMap.cpu().squeeze(0).numpy()
        saliencyMap = torch.FloatTensor(cv2.resize(saliencyMap, (fixationMap.size(2), fixationMap.size(1)))).unsqueeze(
            0)
        # saliencyMap = saliencyMap.cuda()
        # fixationMap = fixationMap.cuda()
    if len(saliencyMap.size()) == 3:
        saliencyMap = saliencyMap[0, :, :]
        fixationMap = fixationMap[0, :, :]
    saliencyMap = saliencyMap.cpu().numpy()
    fixationMap = fixationMap.cpu().numpy()
    if normalize:
        saliencyMap = normalize_map(saliencyMap)

    if not fixationMap.any():
        print('Error: no fixationMap')
        score = float('nan')
        return score

    # make the saliencyMap the size of the image of fixationMap

    if not np.shape(saliencyMap) == np.shape(fixationMap):
        from scipy.misc import imresize
        saliencyMap = imresize(saliencyMap, np.shape(fixationMap))

    # jitter saliency maps that come from saliency models that have a lot of zero values.
    # If the saliency map is made with a Gaussian then it does not need to be jittered as
    # the values are varied and there is not a large patch of the same value. In fact
    # jittering breaks the ordering in the small values!
    if jitter:
        # jitter the saliency map slightly to distrupt ties of the same numbers
        saliencyMap = saliencyMap + np.random.random(np.shape(saliencyMap)) / 10 ** 7

    # normalize saliency map
    saliencyMap = (saliencyMap - saliencyMap.min()) \
                  / (saliencyMap.max() - saliencyMap.min())

    if np.isnan(saliencyMap).all():
        print('NaN saliencyMap')
        score = float('nan')
        return score

    S = saliencyMap.flatten()
    F = fixationMap.flatten()

    Sth = S[F > 0]  # sal map values at fixation locations
    Nfixations = len(Sth)
    Npixels = len(S)

    allthreshes = sorted(Sth, reverse=True)  # sort sal map values, to sweep through values
    tp = np.zeros((Nfixations + 2))
    fp = np.zeros((Nfixations + 2))
    tp[0], tp[-1] = 0, 1
    fp[0], fp[-1] = 0, 1

    for i in range(Nfixations):
        thresh = allthreshes[i]
        aboveth = (S >= thresh).sum()  # total number of sal map values above threshold
        tp[i + 1] = float(i + 1) / Nfixations  # ratio sal map values at fixation locations
        # above threshold
        fp[i + 1] = float(aboveth - i) / (Npixels - Nfixations)  # ratio other sal map values
        # above threshold

    score = np.trapz(tp, x=fp)
    allthreshes = np.insert(allthreshes, 0, 0)
    allthreshes = np.append(allthreshes, 1)

    if toPlot:
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(1, 2, 1)
        ax.matshow(saliencyMap, cmap='gray')
        ax.set_title('SaliencyMap with fixations to be predicted')
        [y, x] = np.nonzero(fixationMap)
        s = np.shape(saliencyMap)
        plt.axis((-.5, s[1] - .5, s[0] - .5, -.5))
        plt.plot(x, y, 'ro')

        ax = fig.add_subplot(1, 2, 2)
        plt.plot(fp, tp, '.b-')
        ax.set_title('Area under ROC curve: ' + str(score))
        plt.axis((0, 1, 0, 1))
        plt.show()

    return score


def auc_shuff(s_map, gt, other_map, splits=100, stepsize=0.1):


    # print(s_map)
    # s_map = s_map.cpu().numpy()
    # print(s_map)
    s_map = normalize_map(s_map)
    if len(s_map.size()) == 3:
        s_map = s_map[0, :, :]
        gt = gt[0, :, :]
        other_map = other_map[0, :, :]
    s_map = s_map.cpu().numpy()
    gt = gt.cpu().numpy()
    other_map = other_map.cpu().numpy()

    num_fixations = np.sum(gt)

    x, y = np.where(other_map == 1)
    other_map_fixs = []
    for j in zip(x, y):
        other_map_fixs.append(j[0] * other_map.shape[0] + j[1])
    ind = len(other_map_fixs)
    assert ind == np.sum(other_map), 'something is wrong in auc shuffle'

    num_fixations_other = min(ind, num_fixations)

    num_pixels = s_map.shape[0] * s_map.shape[1]
    random_numbers = []
    for i in range(0, splits):
        temp_list = []
        t1 = np.random.permutation(ind)
        for k in t1:
            temp_list.append(other_map_fixs[k])
        random_numbers.append(temp_list)

    aucs = []
    # for each split, calculate auc
    for i in random_numbers:
        r_sal_map = []
        for k in i:
            r_sal_map.append(s_map[k % s_map.shape[0] - 1, int(k / s_map.shape[0])])
        # in these values, we need to find thresholds and calculate auc
        thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        r_sal_map = np.array(r_sal_map)

        # once threshs are got
        thresholds = sorted(set(thresholds))
        area = []
        area.append((0.0, 0.0))
        for thresh in thresholds:
            # in the salience map, keep only those pixels with values above threshold
            temp = np.zeros(s_map.shape)
            temp[s_map >= thresh] = 1.0
            num_overlap = np.where(np.add(temp, gt) == 2)[0].shape[0]
            tp = num_overlap / (num_fixations * 1.0)

            # fp = (np.sum(temp) - num_overlap)/((np.shape(gt)[0] * np.shape(gt)[1]) - num_fixations)
            # number of values in r_sal_map, above the threshold, divided by num of random locations = num of fixations
            fp = len(np.where(r_sal_map > thresh)[0]) / (num_fixations * 1.0)

            area.append((round(tp, 4), round(fp, 4)))

        area.append((1.0, 1.0))
        area.sort(key=lambda x: x[0])
        tp_list = [x[0] for x in area]
        fp_list = [x[1] for x in area]

        aucs.append(np.trapz(np.array(tp_list), np.array(fp_list)))

    return np.mean(aucs)

def ig(s_map, gt, baseline):
    batch_size = s_map.size(0)
    w = s_map.size(1)
    h = s_map.size(2)

    sum_s_map = torch.sum(s_map.view(batch_size, -1), 1)
    expand_s_map = sum_s_map.view(batch_size, 1, 1).expand(batch_size, w, h)

    assert expand_s_map.size() == s_map.size()

    sum_gt = torch.sum(gt.view(batch_size, -1), 1)
    expand_gt = sum_gt.view(batch_size, 1, 1).expand(batch_size, w, h)

    assert expand_gt.size() == gt.size()

    sum_baseline = torch.sum(baseline.view(batch_size, -1), 1)
    expand_baseline = sum_baseline.view(batch_size, 1, 1).expand(batch_size, w, h)

    assert expand_baseline.size() == baseline.size()

    s_map = s_map / (expand_s_map * 1.0)
    gt = gt / (expand_gt * 1.0)
    baseline = baseline / (expand_baseline * 1.0)
    s_map = s_map.view(batch_size, -1)
    gt = gt.view(batch_size, -1)
    baseline = baseline.view(batch_size, -1)
    eps = 2.2204e-16
    result = gt * (torch.log(eps + s_map) - torch.log(eps + baseline))

    return torch.mean(torch.sum(result))

def center_bias(img_size):
        width_sigma=0.5
        center_x=0.5
        center_y=0.5
        height = img_size[0]
        width = img_size[1]
        YS, XS = np.mgrid[:height, :width].astype(float)
        XS /= width
        YS /= height
        XS -= center_x
        YS -= center_y
        r_squared = XS**2 + YS**2
        return np.ones((img_size[0], img_size[1]))*np.exp(-0.5*r_squared/(width_sigma)**2)