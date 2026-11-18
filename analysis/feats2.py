import numpy as np, pandas as pd
def sm(x,k=3): return pd.Series(x).rolling(k,center=True,min_periods=1).mean().to_numpy()
def feats2(s,d,hz=10):
    s=np.asarray(s,float); n=len(s)
    if n<15: return None
    du=sm(np.degrees(np.unwrap(np.radians(np.asarray(d,float)))),3); ss=sm(s,3)
    om=np.radians(np.abs(np.gradient(du)*hz)); lat=ss*om; acc=np.gradient(ss)*hz
    # the break: frame of max lateral force once moving fast (after launch)
    ok=(ss>3.0)&(np.arange(n)>8)
    if ok.sum()<4: return None
    k=int(np.argmax(np.where(ok,lat,-1)))
    pre=ss[max(0,k-8):k+1]; vin=pre.max()
    lo=k+int(np.argmin(ss[k:min(n,k+8)])); vmin=ss[lo]
    post=acc[lo:min(n,lo+12)]
    reacc=post.max() if len(post) else np.nan
    win=lat[max(0,k-3):k+4]
    return dict(cut_force=float(np.mean(np.sort(win)[-3:])), entry=float(vin), vmin=float(vmin),
                keep=float(vmin/vin) if vin>0 else np.nan, reaccel=float(reacc),
                dv1=float(ss[min(n-1,lo+10)]-vmin))
