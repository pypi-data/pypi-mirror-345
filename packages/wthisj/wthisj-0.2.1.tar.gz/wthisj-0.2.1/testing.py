import wthisj

# initialize a column perimeter
column1 = wthisj.PunchingShearSection(col_width = 20,
                                      col_depth = 20,
                                      slab_avg_depth = 8,
                                      condition = "W",
                                      overhang_x = 0,
                                      overhang_y = 0,
                                      studrail_length = 0)

# calculate punching shear stress
results = column1.solve(Vz = -80, Mx = 0, My = 1400, consider_ecc=False)

# plot results (plotly)
column1.plot_results_3D()
