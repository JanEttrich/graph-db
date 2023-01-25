from utility import *
def test_box_nodes_plot():
    p1 = np.array([5000, 5000, 5000])
    p2 = np.array([6000, 6000, 6000])
    df = get_nodes_in_box(p1, p2, 500)
    points = convert_df_to_points(df)
    plot_points(points, "test1")

def test_box_loop_fitting():
    p3,p4, _ = fit_box_to_loop(1135, 500)
    new_df = get_nodes_in_box(p3, p4, 500)
    points = convert_df_to_points(new_df)
    plot_points(points, "test2_1")
    p3,p4, _ = fit_box_to_loop(1135, 550)
    new_df = get_nodes_in_box(p3, p4, 550)
    points = convert_df_to_points(new_df)
    plot_points(points, "test2_2")
    p3,p4, _ = fit_box_to_loop(1135, 600)
    new_df = get_nodes_in_box(p3, p4, 600)
    points = convert_df_to_points(new_df)
    plot_points(points, "test2_3")

if __name__ == "__main__":
    #test_box_nodes_plot()
    test_box_loop_fitting()