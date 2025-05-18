from easydict import EasyDict

cfg = EasyDict()

cfg.DATA = EasyDict()
cfg.DATA.RESOLUTION = (352, 352)
# cfg.DATA.RESOLUTION = (512, 512)
# cfg.DATA.SALICON_ROOT = ".\dataset\salicon"
# cfg.DATA.SALICON_TRAIN = ".\dataset\salicon_train.csv"
# cfg.DATA.SALICON_VAL = ".\dataset\salicon_val.csv"
# cfg.DATA.LOG_DIR = "./logs"
# cfg.DATA.RESOLUTION = (512, 512)
cfg.DATA.SALICON_ROOT = "./dataset/salicon"
cfg.DATA.SALICON_TRAIN = "./dataset/salicon_train.csv"
cfg.DATA.SALICON_VAL = "./dataset/salicon_val.csv"
# cfg.DATA.SALICON_ROOT = "./dataset/air_saliency"
# cfg.DATA.SALICON_TRAIN = "./dataset/combined_files_train.csv"
# cfg.DATA.SALICON_VAL = "./dataset/combined_files_val.csv"
cfg.DATA.LOG_DIR = "./logs/test_kl_cc_bce"
# cfg.DATA_LOG_DIR = "./logs/weight6newmodel_test1"
# cfg.DATA_LOG_DIR = "./logs/saliency/test_train_mse_tvd"
cfg.DATA_LOG_DIR = "./logs/saliency/test_kl_cc_bce" #什么都没有的情况
# cfg.DATA_LOG_DIR = "./logs/test_ocrest/"

# cfg.DATA.RESOLUTION = (352, 352)
# cfg.DATA.SALICON_ROOT = "../dataset/salicon"
# cfg.DATA.SALICON_TRAIN = "/media/test_lcl/GSGNet/dataset/salicon_train.csv"
# cfg.DATA.SALICON_VAL = "/media/test_lcl/GSGNet/dataset/salicon_val.csv"
# cfg.DATA.LOG_DIR = "./logs"

# Train
cfg.TRAIN = EasyDict()
cfg.TRAIN.BATCH_SIZE =10

cfg.SOLVER = EasyDict()
cfg.SOLVER.LR = 1e-4
cfg.SOLVER.MIN_LR = 1e-8
cfg.SOLVER.MAX_EPOCH =15