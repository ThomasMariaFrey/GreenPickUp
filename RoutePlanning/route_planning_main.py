import pandas as pd
from route_planning import RoutePlanning


class Main:
    def __init__(self, weight: str = "length"):
        self.df = pd.read_csv("frontenddatasets20230528.csv")
        self.weight = weight
        self.route = RoutePlanning("Stuttgart, Germany", self.df, (48.72905, 9.14477), self.weight)

    def plot_route(self):
        self.route.plot_routes_folium("route_planning_folium.html")


if __name__ == "__main__":
    main = Main()
    main.plot_route()
    main2 = Main(weight="duration")
    main2.plot_route()
