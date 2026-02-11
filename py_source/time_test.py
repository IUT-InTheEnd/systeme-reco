import reco_user_based_p3
from time import time

s = time()

[reco_user_based_p3.get_pred_for_user(8, 155776) for i in range(1000)]

print("time =", time()-s)