# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2022/2/24 
# @Function: 非极大值抑制
import numpy as np


def nms(boxes, iou_thresh=0.8) -> list:
    """
    仅适合单个类别，不适合多类别
    :param boxes: [[scores, x_min, y_min, x_max, y_max]....]
    :param iou_thresh: 交并比的阈值，当大于该阈值时则选优
    :return: [index] boxes的索引
    """
    if isinstance(boxes, list):
        boxes = np.array(boxes)
    x1 = boxes[:, -4].astype(float).astype(int)
    y1 = boxes[:, -3].astype(float).astype(int)
    x2 = boxes[:, -2].astype(float).astype(int)
    y2 = boxes[:, -1].astype(float).astype(int)
    areas = (y2 - y1 + 1) * (x2 - x1 + 1)
    scores = boxes[:, -5].astype(float)
    # 存放nms后剩余的box
    boxes_filter = []
    # 取出分数从大到小排列的索引 .argsort()是从小到大排列，[::-1]是列表头和尾颠倒一下
    index = scores.argsort()[::-1]
    # print('index:',index)
    # 上面这两句比如分数[0.72 0.8  0.92 0.72 0.81 0.9 ]
    #  对应的索引index[  2   5    4     1    3   0  ]
    #  记住是取出索引，scores列表没变
    # index会剔除遍历过的方框，和合并过的box。
    while index.size > 0:
        # print(index.size)
        # 取出第一个方框进行和其他方框比对，看有没有可以合并的
        i = index[0]  # 取出第一个索引号，这里第一个是【2】

        # 因为我们这边分数已经按从大到小排列了。
        # 所以如果有合并存在，也是保留分数最高的这个，也就是我们现在那个这个
        # keep保留的是索引值，不是具体的分数。
        boxes_filter.append(i)
        # print('keep:',keep)
        # print('x1:', x1[i])
        # print(x1[index[1:]])

        # 计算交集的左上角和右下角
        # 这里要注意，比如x1[i]这个方框的左上角x和所有其他的方框的左上角x的
        x11 = np.maximum(x1[i], x1[index[1:]])  # calculate the points of overlap
        y11 = np.maximum(y1[i], y1[index[1:]])
        x22 = np.minimum(x2[i], x2[index[1:]])
        y22 = np.minimum(y2[i], y2[index[1:]])
        # print('*'*20)
        # print(x11, y11, x22, y22)
        # 这边要注意，如果两个方框相交，X22-X11和Y22-Y11是正的。
        # 如果两个方框不相交，X22-X11和Y22-Y11是负的，我们把不相交的W和H设为0.
        w = np.maximum(0, x22 - x11 + 1)
        h = np.maximum(0, y22 - y11 + 1)

        # 计算重叠面积就是上面说的交集面积。不相交因为W和H都是0，所以不相交面积为0
        overlaps = w * h
        # print('overlaps is', overlaps)

        # 这个就是IOU公式（交并比）。
        # 得出来的ious是一个列表，里面拥有当前方框和其他所有方框的IOU结果。
        ious = overlaps / (areas[i] + areas[index[1:]] - overlaps)
        # print('ious is', ious)
        # print(type(ious))

        # 接下来是合并重叠度最大的方框，也就是合并ious中值大于thresh的方框
        # 我们合并的操作就是把他们剔除，因为我们合并这些方框只保留下分数最高的。
        # 我们经过排序当前我们操作的方框就是分数最高的，所以我们剔除其他和当前重叠度最高的方框
        # 这里np.where(ious<=thresh)[0]是一个固定写法。
        idx = np.where(ious <= iou_thresh)[0]
        # print('idx:',idx)
        # print(type(idx))

        # 把留下来框在进行NMS操作
        # 这边留下的框是去除当前操作的框，和当前操作的框重叠度大于thresh的框
        # 每一次都会先去除当前操作框，所以索引的列表就会向前移动移位，要还原就+1，向后移动一位
        index = index[idx + 1]  # because index start from 1
    return boxes_filter


def multi_nms(boxes: list, iou_thresh=None) -> list:
    """
    适合多类别
    :param boxes: [[cls, scores, x_min, y_min, x_max, y_max]....]
    :param iou_thresh: 交并比的阈值，当大于该阈值时则选优
        {   "base": 0.8,
            "cls_1": 0.5,
            "cls_2": 0.5
        }
    :return: [index] boxes的索引
    """
    if iou_thresh is None:
        iou_thresh = {"base": 0.8}
    if isinstance(boxes, list):
        boxes = np.array(boxes)
    classes = boxes[:, -6]
    res_ids = []
    unique_cls = np.unique(classes)
    # 遍历每个类别，进行nms操作
    for cls in unique_cls:
        det = [box for box in boxes if box[0] == cls]
        det_ids = [index for index, box in enumerate(boxes) if box[0] == cls]
        thresh = iou_thresh.get(cls, iou_thresh.get("base"))
        res = nms(boxes=det, iou_thresh=thresh)
        if len(res):
            for i in res:
                res_ids.append(det_ids[i])
    return res_ids


if __name__ == "__main__":
    # boxes_ = np.array([[0.72, 100, 100, 210, 210],
    #                   [0.80, 250, 250, 420, 420],
    #                   [0.92, 220, 220, 320, 330],
    #                   [0.72, 100, 100, 210, 210],
    #                   [0.81, 230, 240, 325, 330],
    #                   [0.90, 220, 230, 315, 340]])
    # print(nms(boxes_, iou_thresh=0.7))
    boxes_ = np.array([["1", 0.72, 100, 100, 210, 210],
                      ["1", 0.80, 250, 250, 420, 420],
                      ["1", 0.92, 220, 220, 320, 330],
                      ["2", 0.72, 100, 100, 210, 210],
                      ["2", 0.81, 230, 240, 325, 330],
                      ["2", 0.90, 220, 230, 315, 340]]).tolist()
    print(multi_nms(boxes_, iou_thresh={"base": 0.5, "1": 0.7, "2": 0.9}))

