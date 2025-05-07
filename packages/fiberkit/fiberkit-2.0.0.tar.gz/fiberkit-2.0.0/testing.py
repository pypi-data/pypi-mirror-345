import fiberkit as fkit

# define some fibers we will use later
fiber_unconfined       = fkit.patchfiber.Todeschini(fpc=5, eo=0.002, emax=0.006, default_color="lightgray")
fiber_confined         = fkit.patchfiber.Mander(fpc=6, eo=0.004, emax=0.014, default_color="gray")
fiber_structural_steel = fkit.patchfiber.Multilinear(fy=50, fu=80, Es=29000, default_color="steelblue")
fiber_rebar            = fkit.nodefiber.Bilinear(fy=60, fu=75, Es=29000, emax=0.16, default_color="black")


# W_AISC
section10 = fkit.sectionbuilder.W_AISC(
    shape = "W27X307",
    steel_fiber = fiber_structural_steel)

fiber_concrete = fkit.patchfiber.Hognestad(fpc=4, take_tension=True)
fiber_steel    = fkit.nodefiber.Bilinear(fy=60, Es=29000)

# create a rectangular beam section with SectionBuilder
section1 = fkit.sectionbuilder.rectangular(width = 18, 
                                           height = 24, 
                                           cover = 2, 
                                           top_bar = [0.6, 4, 1, 0], #[bar_area, nx, ny, y_spacing]
                                           bot_bar = [0.6, 4, 2, 3], #[bar_area, nx, ny, y_spacing] 
                                           concrete_fiber = fiber_concrete, 
                                           steel_fiber = fiber_steel,
                                           mesh_nx=0.75,
                                           mesh_ny=0.75)


# moment curvature
MK_results = section1.run_moment_curvature(phi_target=0.0003)
fkit.plotter.plot_MK_3D(section1)

