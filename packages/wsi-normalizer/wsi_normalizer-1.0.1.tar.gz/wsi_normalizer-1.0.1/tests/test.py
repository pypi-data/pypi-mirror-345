import cv2
from wsi_normalizer import MacenkoNormalizer, ReinhardNormalizer, VahadaneNormalizer, TorchVahadaneNormalizer, imread

# 设置图像路径
img_path = r'D:\Github\wsi-normalizer\tests\eg_slide_1\eg_2.jpg'
target_path = r'D:\Github\wsi-normalizer\tests\eg_slide_1\eg_1.jpg'

# 读取图像
img = imread(img_path)
target = imread(target_path)

# 初始化归一化器
mnormalizer = MacenkoNormalizer()
rnormalizer = ReinhardNormalizer()
vnormalizer = TorchVahadaneNormalizer()

# 拟合归一化器
mnormalizer.fit(img)
rnormalizer.fit(img)
vnormalizer.fit(img)

# 对目标图像进行归一化
m = mnormalizer.transform(target)
r = rnormalizer.transform(target)
v = vnormalizer.transform(target)

# 保存归一化后的图像
cv2.imwrite('m1.jpg', cv2.cvtColor(m, cv2.COLOR_RGB2BGR))
cv2.imwrite('r1.jpg', cv2.cvtColor(r, cv2.COLOR_RGB2BGR))
cv2.imwrite('v1.jpg', cv2.cvtColor(v, cv2.COLOR_RGB2BGR))
