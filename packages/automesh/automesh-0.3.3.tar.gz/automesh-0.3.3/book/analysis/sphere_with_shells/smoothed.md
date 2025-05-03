# Smoothed Mesh

```sh
alias automesh='~/autotwin/automesh/target/release/automesh'
```

```sh
cd ~/autotwin/automesh/book/analysis/sphere_with_shells
```

## Taubin Smoothing

`sr2s10` | `sr2s50`
:---: | :---:
![](img/sr2s10.png) | ![](img/sr2s50.png)

Smooth with various number of iterations:

```sh
automesh mesh hex \
--remove 0 \
--xscale 0.5 --yscale 0.5 --zscale 0.5 \
--xtranslate -12 --ytranslate -12 --ztranslate -12 \
--input spheres_resolution_2.npy \
--output sr2s10.exo \
smooth \
--hierarchical \
--iterations 10
```

```sh
automesh mesh hex \
--remove 0 \
--xscale 0.5 --yscale 0.5 --zscale 0.5 \
--xtranslate -12 --ytranslate -12 --ztranslate -12 \
--input spheres_resolution_2.npy \
--output sr2s50.exo \
smooth \
--hierarchical \
--iterations 50
```

## Quality Metrics

Assess element quality to avoid oversmoothing:

```sh
automesh mesh hex \
--remove 0 \
--xscale 0.5 --yscale 0.5 --zscale 0.5 \
--xtranslate -12 --ytranslate -12 --ztranslate -12 \
--input spheres_resolution_2.npy \
--output sr2s10.inp \
smooth \
--hierarchical \
--iterations 10

automesh metrics \
--input sr2s10.inp \
--output sr2s10.csv
```

```sh
automesh mesh hex \
--xscale 0.5 --yscale 0.5 --zscale 0.5 \
--xtranslate -12 --ytranslate -12 --ztranslate -12 \
--input spheres_resolution_2.npy \
--output sr2s50.inp \
smooth \
--hierarchical \
--iterations 50

automesh metrics \
--input sr2s50.inp \
--output sr2s50.csv
```

With [`figio`](https://pypi.org/project/figio/) and
the [`hist_sr2sx.yml`](recipes/hist_sr2sx.yml) recipe,

```sh
cd ~/autotwin/automesh/book/analysis/sphere_with_shells/recipes
figio hist_sr2sx.yml
```
we obtain the following element quality metrics:

![hist_sr2sx_aspect.png](img/hist_sr2sx_aspect.png)

![hist_sr2sx_msj.png](img/hist_sr2sx_msj.png)

![hist_sr2sx_skew.png](img/hist_sr2sx_skew.png)

![hist_sr2sx_vol.png](img/hist_sr2sx_vol.png)
