import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
import matplotlib
matplotlib.rcParams['animation.embed_limit'] = 2**128
def plot_joint_density_animation(
        adata, 
        estimator, 
        t_min=0.01, 
        t_max=0.99,  
        lower_bound=-1000,  
        basis='umap', 
        n_frame=50, 
        cmap='viridis', 
        s=.5, 
        show_text=True, 
        show=True, 
        save_path=None,
        **kwargs 
    ):
    

    """plot the animation of joint density log P (x,t)

        Arguments:
        ---------
        adata: :class:`~anndata.AnnData`
            Annotated data matrix.
        estimator: :class:`~pygot.tl.analysis.ProbabilityModel` 
            Density Estimator
        t_min: `float` (default: 0.01)
            Start time
        t_max: `float` (default: 0.99)
            End time
        lower_bound: `float` (default: -1000)
            Lower bound of log-density
        basis: `str` (default: 'umap')
            Visulization space
        n_frame: `int` (default: 50)
            Number of animation frames
        cmap: `str` (default: 'viridis')
            Color map
        s: `float` (default: 0.5)
            Volume of scatter
        show_text: `bool` (default: True)
            Show the text of current density
        show: `bool` (default: True)
            Show in the jupyter notebook
        save_path: `str` (default: None)
            Path for animation saved
        **kwargs 
            kwargs of matplotlib.pyplot.scatter
        
        
        """
    fig, ax = plt.subplots()
    log_pxt = estimator.log_prob_x_t(adata,  t_min, lower_bound=lower_bound).flatten()

    scatter = ax.scatter(adata.obsm['X_'+basis][:,0], adata.obsm['X_'+basis][:,1],  c=(log_pxt - np.min(log_pxt)) / (np.max(log_pxt) - np.min(log_pxt)), 
                    cmap=cmap, s=s, **kwargs)
    ax.axis('off')
    plt.close()
    if show_text:
        frame_text = ax.text(0.02, 0.95, 'log P(t={:.2f} | x)'.format(t_min), transform=ax.transAxes, fontsize=12)

    def update(frame):

        i = np.linspace(t_min,t_max,n_frame)[frame]
        log_pxt = estimator.log_prob_x_t(adata,  i, lower_bound=lower_bound).flatten()
        
        if show_text:
            frame_text.set_text('log P(t={:.2f}|x)'.format(i))
        
        scatter.set_array((log_pxt - np.min(log_pxt)) / (np.max(log_pxt) - np.min(log_pxt)))  # 更新散点的颜色
        return scatter,


    ani = FuncAnimation(fig, update, frames=range(n_frame), blit=True)    
    if not (save_path is None):
        ani.save(save_path, writer='imagemagick')
    if show:
        return HTML(ani.to_jshtml())
    

def plot_conditional_density_animation(
        adata, 
        estimator, 
        t_min=0.01, 
        t_max=0.99,  
        lower_bound=-1000,  
        basis='umap', 
        n_frame=50, 
        cmap='viridis', 
        s=.5, 
        show_text=True, 
        show=True, 
        save_path=None,
        **kwargs 
    ):
    

    """plot the animation of conditional density log P (t|x)

        Arguments:
        ---------
        adata: :class:`~anndata.AnnData`
            Annotated data matrix.
        estimator: :class:`~pygot.tl.analysis.ProbabilityModel` 
            Density Estimator
        t_min: `float` (default: 0.01)
            Start time
        t_max: `float` (default: 0.99)
            End time
        lower_bound: `float` (default: -1000)
            Lower bound of log-density
        basis: `str` (default: 'umap')
            Visulization space
        n_frame: `int` (default: 50)
            Number of animation frames
        cmap: `str` (default: 'viridis')
            Color map
        s: `float` (default: 0.5)
            Volume of scatter
        show_text: `bool` (default: True)
            Show the text of current density
        show: `bool` (default: True)
            Show in the jupyter notebook
        save_path: `str` (default: None)
            Path for animation saved
        **kwargs 
            kwargs of matplotlib.pyplot.scatter
        
        
        """
    fig, ax = plt.subplots()
    log_pxt = estimator.log_prob_t_given_x(adata,  t_min,  lower_bound=lower_bound).flatten()

    scatter = ax.scatter(adata.obsm['X_'+basis][:,0], adata.obsm['X_'+basis][:,1],  c=(log_pxt - np.min(log_pxt)) / (np.max(log_pxt) - np.min(log_pxt)), 
                    cmap=cmap, s=s, **kwargs)
    ax.axis('off')
    plt.close()
    if show_text:
        frame_text = ax.text(0.02, 0.95, 'log P(t={:.2f} | x)'.format(t_min), transform=ax.transAxes, fontsize=12)

    def update(frame):

        i = np.linspace(t_min,t_max,n_frame)[frame]
        log_pxt = estimator.log_prob_t_given_x(adata,  i,  lower_bound=lower_bound).flatten()
        
        if show_text:
            frame_text.set_text('log P(t={:.2f}|x)'.format(i))
        
        scatter.set_array((log_pxt - np.min(log_pxt)) / (np.max(log_pxt) - np.min(log_pxt)))  # 更新散点的颜色
        return scatter,


    ani = FuncAnimation(fig, update, frames=range(n_frame), blit=True)    
    if not (save_path is None):
        ani.save(save_path, writer='imagemagick')
    if show:
        return HTML(ani.to_jshtml())
