import fiberkit as fkit

# define concrete and steel fibers
fiber_concrete = fkit.patchfiber.Hognestad(fpc=4, take_tension=True)
fiber_steel    = fkit.nodefiber.Bilinear(fy=60, Es=29000)

# create a rectangular beam section with SectionBuilder
section1 = fkit.sectionbuilder.rectangular(width = 18, 
                                           height = 24, 
                                           cover = 2, 
                                           top_bar = [0.6, 4, 1, 0], #[bar_area, nx, ny, y_spacing]
                                           bot_bar = [0.6, 4, 2, 3], #[bar_area, nx, ny, y_spacing] 
                                           concrete_fiber = fiber_concrete, 
                                           steel_fiber = fiber_steel)

# moment curvature
MK_results = section1.run_moment_curvature(phi_target=0.0003)
df_nodefibers, df_patchfibers = section1.get_all_fiber_data()

# cracked moment of inertia
Icr_results = section1.calculate_Icr(Es=29000, Ec=3605)

# PM Interaction surface analysis
PM_results = section1.run_PM_interaction(fpc=4, fy=60, Es=29000)

# plot results
fkit.plotter.plot_MK(section1)
fkit.plotter.plot_PM(section1)
fkit.plotter.plot_Icr(section1)
fkit.plotter.plot_MK_3D(section1) # NEW IN VERSION 2.0.0

