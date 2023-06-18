"""
Copright © 2023 Howard Hughes Medical Institute, Authored by Carsen Stringer and Marius Pachitariu.
"""
import matplotlib.pyplot as plt 
import os
import numpy as np
from rastermap.utils import bin1d
import metrics
from fig_utils import *

def panels_schematic(fig, grid, il, cc_tdelay, tshifts, BBt_log, BBt_travel, 
                     U_nodes, U_upsampled, kmeans_img):
    dx = 0.1
    dy = 0.1
    xpad = 0.96 / 5
    transl = mtransforms.ScaledTranslation(-18 / 72, 7 / 72, fig.dpi_scale_trans)
    
    ### schematics
    ax_kmeans = plt.subplot(grid[0,0])
    ax_kmeans.axis("off")
    il = plot_label(ltr, il, ax_kmeans, transl, fs_title)
    pos = ax_kmeans.get_position().bounds
    x0 = pos[0]-(xpad-dx)/4
    #print(x0)
    ax_kmeans_img = fig.add_axes([x0+0.01, pos[1]+0.5*pos[3], pos[2]*0.3, pos[3]*0.3])
    ax_crosscorr = fig.add_axes([pos[0]+0.55*pos[2], pos[1]+0.4*pos[3], pos[2]*0.3, pos[3]*0.3])

    # plot kmeans illustration
    ax_kmeans_img.imshow(kmeans_img)
    ax_kmeans_img.set_title("k-means\nclustering")
    ax_kmeans_img.axis("off")

    # plot example crosscorr
    c0, c1 = 1, 4
    ax_crosscorr.plot(tshifts, cc_tdelay[c0,c1], color=[0.5,0.5,0.5], zorder=1)
    ax_crosscorr.set_ylabel("corr")
    ax_crosscorr.set_xlabel("time lag ($\delta$t)")
    ax_crosscorr.set_xlim([tshifts.min(), tshifts.max()])
    ax_crosscorr.set_title(f"cross-corr\nclusters {c0}, {c1}")
    ix = cc_tdelay[c0,c1].argmax()
    ax_crosscorr.scatter(tshifts[ix], cc_tdelay[c0,c1,ix], marker="*", lw=0.5, color=[1,0.5,0], s=40, zorder=2)
    ax_crosscorr.text(tshifts[ix]+5, cc_tdelay[c0,c1,ix], "max", color=[1,0.5,0], va="center")
    ax_crosscorr.set_ylim([-0.2,0.9])

    nshow=20
    ax = plt.subplot(grid[0,1]) 
    il = plot_label(ltr, il, ax, transl, fs_title)
    pos = ax.get_position().bounds
    ax.axis("off")
    ax.set_title("time-lagged correlations")
    pos = ax.get_position().bounds
    dym=0.02
    dxm = dym
    np.random.seed(2)
    isort = np.random.permutation(nshow)
    for i in range(3):
        axi = fig.add_axes([pos[0]+(2-i)*dxm-0.1*pos[2], pos[1]+(-i)*dym+0.3*pos[3], pos[2]*0.7, pos[3]*0.7])
        im=axi.imshow(cc_tdelay[c0:c0+nshow, c0:c0+nshow,11+(2-i)][np.ix_(isort, isort)],#[:nshow,:nshow], 
                        vmin=-1, vmax=1, cmap="RdBu_r")
        axi.set_yticks([])
        axi.set_xticks([])
        axi.spines["right"].set_visible(True)
        axi.spines["top"].set_visible(True)
        axi.text(1.05, -0.0, f"$\delta$t = {2-i}", transform=axi.transAxes, ha="left")
        if i==0:
            posi = axi.get_position().bounds
            #divider = make_axes_locatable(ax)
            cax = fig.add_axes([posi[0]+posi[2]+0.005, posi[1]+posi[3]*0.75, posi[2]*0.05, posi[3]*0.25])
            plt.colorbar(im, cax)
        elif i==2:
            axi.text(-.15,0.5,"clusters", transform=axi.transAxes, rotation=90, va="center")
            axi.text(0.5,-0.15,"clusters", transform=axi.transAxes, ha="center")

    ax = plt.subplot(grid[0,2])
    il = plot_label(ltr, il, ax, transl, fs_title)
    ax.set_title("matching matrix")
    ax.axis("off")
    pos = ax.get_position().bounds
    for i,mat in enumerate([BBt_log, BBt_travel]):
        axi = fig.add_axes([pos[0]-dx*0.05+i*dx*1, 
                                    pos[1]+pos[3]*0.3-i*dy*0.3, pos[2]*0.5, pos[3]*0.5])
        axi.imshow(mat[:nshow,:nshow], vmin=-6, vmax=6, cmap="RdBu_r")
        axi.set_yticks([])
        axi.set_xticks([])
        axi.spines["right"].set_visible(True)
        axi.spines["top"].set_visible(True)
        axi.set_title(["global", "traveling\nsalesman"][i])
        if i==0:
            axi.text(1.2,0.25, "+",transform=axi.transAxes, fontsize=default_font+4)

    ax = plt.subplot(grid[0,3])
    il = plot_label(ltr, il, ax, transl, fs_title)
    nn = cc_tdelay.shape[0]
    cc_tdelay[np.arange(0, nn), np.arange(0, nn)] = 1
    im=ax.imshow(cc_tdelay[c0:c0+nshow,c0:c0+nshow,10:].max(axis=-1), vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_title("sorted matrix")
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines["right"].set_visible(True)
    ax.spines["top"].set_visible(True)
    posi = ax.get_position().bounds
    #divider = make_axes_locatable(ax)
    cax = fig.add_axes([posi[0]+posi[2]*1.02, posi[1]+posi[3]*0.75, posi[2]*0.05, posi[3]*0.25])
    plt.colorbar(im, cax)

    ax = plt.subplot(grid[0,4])
    il = plot_label(ltr, il, ax, transl, fs_title)
    for i in range(3):
        nshow=20
        du = 0.4
        p = ax.plot(np.linspace(0, len(U_upsampled[c0:c0+nshow*10,i]), 
                                            len(U_nodes[c0:c0+nshow+1,i])), 
                            U_nodes[c0:c0+nshow+1,i] + du*(2-i), "x", markersize=6, 
                            color=np.ones(3)*(0.25*i),
                            lw=4)
        ax.plot(U_upsampled[c0*10:(c0+nshow)*10,i] + du*(2-i), color=p[0].get_color(), lw=1)
        ax.text(20*10, du*(2-i) + du*0.05 + U_nodes[c0:c0+nshow,i].max(), f"PC {i+1:d}", 
                         color=p[0].get_color(), ha="right")
    ax.set_ylim([-du*0.8,du*2.4])
    ax.axis("off")
    ax.text(0,0.1, "clusters sorted x", transform=ax.transAxes)
    ax.text(0,0., "upsampled nodes -", transform=ax.transAxes)
    ax.text(-0.1,0.5, "weights", rotation=90, transform=ax.transAxes, va="center")
    ax.set_title("upsampling")

    return il

def plot_raster(ax, X, xmin, xmax, vmax=1.5, cax=None, nper=30, label=True):
    xr = xmax - xmin
    nn = X.shape[0]
    im = ax.imshow(X[:, xmin:xmax], vmin=0, vmax=vmax, 
              cmap="gray_r", aspect="auto")
    ax.axis("off")
    ax.plot(-0.005*xr * np.ones(2), nn - np.array([0, 500/nper]), color="k")
    ax.plot(np.array([0, 200]), nn*1.02 + np.zeros(2), color="k")
    ax.set_ylim([0, nn*1.025])
    ax.set_xlim([-0.008*xr, xr])
    ax.invert_yaxis()
    if cax is not None:
        plt.colorbar(im, cax, orientation="horizontal")
        cax.set_xlabel("z-scored\n ")
    if label:
        ht=ax.text(-0.008*xr, X.shape[0], "500 neurons", ha="right")
        ht.set_rotation(90)
        ax.text(0, nn*1.1, "10 sec.")

def panels_raster(fig, grid, il, yratio, X_embs, cc_embs, div_map, mod_names, emb_cols):
    transl = mtransforms.ScaledTranslation(-18 / 72, 7 / 72, fig.dpi_scale_trans)
    
    titles = [" simulated neurons sorted by rastermap", " simulated neurons sorted by t-SNE"]
    mod_names_sort = np.array(mod_names.copy())[np.array([2,0,3,4,1])]
    for k in range(2):
        ax = plt.subplot(grid[k+1,0:3])
        pos = ax.get_position().bounds
        ax.set_position([pos[0], pos[1], pos[2]*0.94, pos[3]])
        pos = ax.get_position().bounds
        if k==0:
            il = plot_label(ltr, il, ax, transl, fs_title)
            cax = fig.add_axes([pos[0]+pos[2]-pos[3]*0.25, pos[1]-pos[3]*0.05, pos[3]*0.25, pos[2]*0.01])
        else:
            cax = None
        plot_raster(ax, X_embs[k], xmin=0, xmax=8000, label=1-k, cax=cax)
        #ax.text(0.05, 1.02, titles[k], transform=ax.transAxes, ha="left", fontsize="large")
        ax.set_title(titles[k])
        if k==0: 
            # create bar with colors 
            cax = fig.add_axes([pos[0]+pos[2]*1.01, pos[1], pos[2]*0.01, pos[3]])
            nn = X_embs[k].shape[0]
            cax.imshow(emb_cols[:,np.newaxis], aspect="auto")
            cax.set_ylim([0, nn*1.025])
            cax.invert_yaxis()
            cax.axis("off")

            # create bar with ticks 
            cax = fig.add_axes([pos[0]+pos[2]*1.03, pos[1], pos[2]*0.01, pos[3]])
            for d in range(len(div_map)):
                cax.plot([0,0], [div_map[d][0], div_map[d][1]], marker=0, color="k")
                cax.text(0.08, (div_map[d][1]-div_map[d][0])/2 + div_map[d][0], 
                         mod_names_sort[d], va="center")
            cax.set_ylim([0, nn*1.025])
            cax.invert_yaxis()
            cax.axis("off")

        ax = plt.subplot(grid[k+1,3])
        pos2 = ax.get_position().bounds
        ax.set_position([pos2[0], pos2[1], pos[3]/yratio, pos[3]])
        vmax = 0.3
        cc = cc_embs[k].copy()
        im = ax.imshow(cc, vmin=-vmax, vmax=vmax, cmap="RdBu_r")
        ax.spines["right"].set_visible(True)
        ax.spines["top"].set_visible(True)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_ylim([0, nn*1.025])
        posi = ax.get_position().bounds
        if k==0:
            ax.set_title("sorted matrix")
            il = plot_label(ltr, il, ax, transl, fs_title)
            cax = fig.add_axes([posi[0], posi[1]-posi[3]*0.05, posi[3]*0.25, posi[2]*0.05])
            plt.colorbar(im, cax, orientation="horizontal")
            cax.set_xticks([-0.3,0,0.3])
        ax.set_ylim([0, nn*1.025])
        ax.set_xlim([0, nn*1.025])
        ax.invert_yaxis()
        ax.axis("off")

    return il

def panels_responses(grid, transl, il, div_map, seqcurves0, seqcurves1, tcurves, xresp, 
                     emb_cols, mod_names):
    mod_names_sort = np.array(mod_names.copy())[np.array([2,0,3,4,1])]
    ax = plt.subplot(grid[1:3, 4])
    pos = ax.get_position().bounds
    ax.set_position([pos[0]-0.02, pos[1]+pos[3]*0.1, pos[2]+0.03, pos[3]*0.8])
    ax.axis("off")
    grid1 = matplotlib.gridspec.GridSpecFromSubplotSpec(2,2, subplot_spec=ax, 
                                                        wspace=0.1, hspace=0.5)
    ax.remove()

    ids = [0, 1, 2, 4]
    nsp = [4, 3, 4, 4]
    xlabels = ["position", "stim id", "position", "time (sec.)"]
    for a in range(4):
        ax = plt.subplot(grid1[a//2,a%2])
        if a==0:
            il = plot_label(ltr, il, ax, transl, fs_title)
        dt = ids[a]
        n_x = div_map[dt][1] - div_map[dt][0]
        if a==0 or a==2:
            tc = seqcurves0.copy() if a==0 else seqcurves1.copy()
            tc = tc[div_map[dt][0] : div_map[dt][1]]
            ax.set_xticks([0,25,50])
        elif a==1:
            tc = tcurves[div_map[dt][0] : div_map[dt][1]].copy()
            ax.set_xticks(np.arange(0,16,5))
        elif a==3:
            tc = xresp[div_map[dt][0] : div_map[dt][1]].copy()
            tc = bin1d(tc, 10, axis=1)
            ax.set_xticks([0, 20])
            ax.set_xticklabels(["0", "10"])
        tc -= tc.min(axis=0)
        if a < 3:
            tc /= tc.max(axis=0)
        for i, c in enumerate(tc[(a<3)::nsp[a]]):
            ax.plot(c, lw=1, color=emb_cols[div_map[dt][0] + i*nsp[a] + (a<3)]);
        ax.set_xlabel(xlabels[a])
        ax.set_title(mod_names_sort[dt], fontsize="medium")
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        if a==0: 
            ax.text(1.1, 1.35, "superneuron responses", transform=ax.transAxes, 
                    ha="center", fontsize="large")
    return il 

def panels_embs(grid, transl, il, xi_all, embs_all, alg_cols, mod_names):
    ax = plt.subplot(grid[3, :3])
    pos = ax.get_position().bounds
    ax.set_position([pos[0]-0.0, pos[1]-0.02, pos[2]-0.02, pos[3]])
    ax.remove()
    grid1 = matplotlib.gridspec.GridSpecFromSubplotSpec(1, 6, subplot_spec=ax, 
                                                    wspace=0.11, hspace=0.2)
    alg_names = ["rastermap", "t-SNE", "UMAP", "isomap", "laplacian\neigenmaps"]
    xip = xi_all.copy()
    embs = embs_all.copy()
    xip = metrics.emb_to_idx(xip)
    ax = plt.subplot(grid1[0])
    il = plot_label(ltr, il, ax, transl, fs_title)
    ht=ax.text(0, 3000, "ground-truth", va="center")
    ht.set_rotation(90)
    ax.text(0, 7000, "benchmarking embedding algorithms", fontsize="large")
    for k in range(5):
        ax.text(len(xip), 1000*k + 500 + 500*(k>3), mod_names[k], ha="right")
        #ax.plot([0, len(xip)], (i+1) * 1000 * np.ones(2), "--", color="k")
    #ax.axis("square")
    ax.set_ylim([0, len(xip)])
    ax.set_xlim([0, len(xip)])
    ax.axis("off")
    
    for k in range(5):
        ax = plt.subplot(grid1[k+1])
        idx = metrics.emb_to_idx(embs[k])
        ax.scatter(idx, xip, s=1, alpha=0.05, color=alg_cols[k])
        for i in range(4):
            ax.plot([0, len(xip)], (i+1) * 1000 * np.ones(2), "--", color="k", lw=0.5)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.spines["right"].set_visible(True)
        ax.spines["top"].set_visible(True)
        ax.set_title(alg_names[k], color=alg_cols[k], fontsize="medium")
        ax.set_ylim([0, len(xip)])
        ax.set_xlim([0, len(xip)])
        if k==2:
            ax.text(0.5, -0.15, "embedding position", transform=ax.transAxes, ha="center")

    return il

def panels_scores(grid, transl, il, scores_all, alg_cols, mod_names):
    ts = 100 * scores_all[:,1].mean(axis=0)
    ts_sem = 100 * scores_all[:,1].std(axis=0) / (scores_all.shape[0]-1)**0.5
    cs = 100 * scores_all[:,0].mean(axis=0)
    cs_sem = 100 * scores_all[:,0].std(axis=0) / (scores_all.shape[0]-1)**0.5

    ax = plt.subplot(grid[3,3])
    il = plot_label(ltr, il, ax, transl, fs_title)
    for k in range(5):
        ax.errorbar(np.arange(5), ts[k], ts_sem[k], lw=2,
                    color=alg_cols[k], zorder=0 if k>0 else 5)
    ax.plot(100 * np.ones(5) / 3., color="k", linestyle="--")
    ax.text(0, 33, "chance", va="top")
    ax.set_ylabel("% correct triplets")
    ax.set_ylim([28, 83])
    ax.set_xticks(np.arange(0, 5))
    ax.set_xticklabels(mod_names, 
                        rotation=30, ha="right", rotation_mode="anchor")

    ax = plt.subplot(grid[3,4])
    il = plot_label(ltr, il, ax, transl, fs_title)
    for k in range(5):
        ax.errorbar(np.arange(5), cs[k], cs_sem[k], lw=2, 
                    color=alg_cols[k], zorder=0 if k>0 else 5)
    ax.plot(100 * np.array([5./6, 5./6, 5./6, 5./6, 2./3]), color="k", linestyle="--")
    ax.text(0, 85, "chance")
    ax.set_ylabel("% contamination")
    ax.set_xticks(np.arange(0, 5))
    ax.set_xticklabels(mod_names, 
                        rotation=30, ha="right", rotation_mode="anchor")
    return il

def _fig1(kmeans_img, xi_all, cc_tdelay, tshifts, BBt_log, BBt_travel, 
        seqcurves0, seqcurves1, tcurves, xresp, 
        U_nodes, U_upsampled, X_embs, cc_embs,cc_embs_max,
        csig, scores_all, embs_all):
    
    fig = plt.figure(figsize=(14,12))
    yratio = 14 / 12
    grid = plt.GridSpec(4,5, figure=fig, left=0.04, right=0.98, top=0.96, bottom=0.07, 
                        wspace = 0.35, hspace = 0.3)

    alg_cols = plt.get_cmap("tab20b")(np.linspace(0,1.,20))[::4]
    alg_cols = np.concatenate((np.array([0,0,0,1])[np.newaxis,:],
                               alg_cols), axis=0)

    # divide up plot into modules
    div_map = [[0, 35], [35, 63], [67, 102], [106, 172], [174, 196]]
    mod_names = ["tuning", "sustained", "sequence 1", "sequence 2", "power-law"]

    il = 0
    il = panels_schematic(fig, grid, il, cc_tdelay, tshifts, BBt_log, BBt_travel, 
                         U_nodes, U_upsampled, kmeans_img)

    emb_cols = plt.get_cmap("gist_ncar")(np.linspace(0.05, 0.95, X_embs[0].shape[0]))[::-1]
    il = panels_raster(fig, grid, il, yratio, X_embs, cc_embs_max, div_map, mod_names, emb_cols)

    transl = mtransforms.ScaledTranslation(-18 / 72, 40 / 72, fig.dpi_scale_trans)
    il = panels_responses(grid, transl, il, div_map, seqcurves0, seqcurves1, tcurves, xresp, 
                        emb_cols, mod_names)

    transl = mtransforms.ScaledTranslation(-18 / 72, 26 / 72, fig.dpi_scale_trans)
    il = panels_embs(grid, transl, il, xi_all, embs_all, alg_cols, mod_names)

    transl = mtransforms.ScaledTranslation(-40 / 72, 7 / 72, fig.dpi_scale_trans)
    panels_scores(grid, transl, il, scores_all, alg_cols, mod_names)

    return fig 

def fig1(root, save_figure=True):
    d1 = np.load(os.path.join(root, "simulations", "sim_results.npz"), allow_pickle=True) 
    d2 = np.load(os.path.join(root, "simulations", "sim_performance.npz"), allow_pickle=True) 
    try:
        kmeans_img = plt.imread(os.path.join(root, "figures", "manifold_kmeans.png"))
    except:
        kmeans_img = np.zeros((50,50))

    fig = _fig1(kmeans_img, **d1, **d2);
    if save_figure:
        fig.savefig(os.path.join(root, "figures", "fig1.pdf"))

            


        