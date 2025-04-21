import tkinter as tk
from tkinter import ttk
import googlemaps
import webbrowser
import folium

def find_optimal_route(origin, destination, api_key, mode="driving", avoid=None):

    gmaps = googlemaps.Client(key=api_key)

    directions_result = gmaps.directions(
        origin,
        destination,
        mode=mode,
        avoid=avoid,
        alternatives=True 
    )

    if not directions_result:
        return None, []

    routes = []
    for route in directions_result:
        distance = route['legs'][0]['distance']['value']
        time = route['legs'][0]['duration']['value']
        traffic = 1.0 
        road_condition = 1.0
        routes.append({
            'distance': distance,
            'time': time,
            'traffic': traffic,
            'road_condition': road_condition,
            'summary': route['summary'],
            'google_maps_route': route,
        })

    queue = []
    for route in routes:
        adjusted_time = route['time'] * route['traffic'] * route['road_condition']
        score = route['distance'] + adjusted_time
        queue.append((score, route))
    queue.sort()

    optimal_route = queue[0][1] 
    return optimal_route, routes


def show_results(optimal_route, all_routes):
    result_window = tk.Toplevel(root)
    result_window.title("Route Optimization Results")

    ttk.Label(result_window, text="Optimal Route:", font=("Helvetica", 14, "bold")).pack(pady=10)
    ttk.Label(result_window, text=f"Summary: {optimal_route['summary']}", wraplength=500).pack()
    ttk.Label(result_window, text=f"Distance: {optimal_route['distance'] / 1000:.2f} km").pack()
    ttk.Label(result_window, text=f"Estimated time: {optimal_route['time'] / 60:.2f} minutes").pack()

    map_center = [
        optimal_route['google_maps_route']['legs'][0]['start_location']['lat'],
        optimal_route['google_maps_route']['legs'][0]['start_location']['lng']
    ]
    m = folium.Map(location=map_center, zoom_start=12)

    route_coordinates = []
    for step in optimal_route['google_maps_route']['legs'][0]['steps']:
        start_lat = step['start_location']['lat']
        start_lng = step['start_location']['lng']
        end_lat = step['end_location']['lat']
        end_lng = step['end_location']['lng']
        route_coordinates.extend([[start_lat, start_lng], [end_lat, end_lng]])

    folium.PolyLine(route_coordinates,
                    color="blue",
                    weight=5,
                    opacity=1,
                    tooltip="Optimal Route").add_to(m)

    folium.Marker(location=[
        optimal_route['google_maps_route']['legs'][0]['start_location']['lat'],
        optimal_route['google_maps_route']['legs'][0]['start_location']['lng']
    ],
                  popup="Origin",
                  tooltip="Origin",
                  icon=folium.Icon(color="green")).add_to(m)
    
    folium.Marker(location=[
        optimal_route['google_maps_route']['legs'][0]['end_location']['lat'],
        optimal_route['google_maps_route']['legs'][0]['end_location']['lng']
    ],
                  popup="Destination",
                  tooltip="Destination",
                  icon=folium.Icon(color="red")).add_to(m)

    map_file = "optimal_route_map.html"
    m.save(map_file)

    webbrowser.open_new(map_file)

    ttk.Label(result_window, text="All Possible Routes:", font=("Helvetica", 14, "bold")).pack(pady=10)
    route_listbox = tk.Listbox(result_window, width=80)
    for i, route in enumerate(all_routes):
        route_listbox.insert(tk.END, f"Route {i+1}: {route['summary']}")
    route_listbox.pack()

def optimize_route():
    origin = origin_entry.get()
    destination = destination_entry.get()
    api_key ="AIzaSyBf71hDbQqaHfcrecu9UbgL1NpY3WlooGc"

    optimal_route, all_routes = find_optimal_route(origin, destination, api_key)

    if optimal_route:
        show_results(optimal_route, all_routes)
    else:
        print("No routes found.")

root = tk.Tk()
root.title("Smart Navigation Assistant")

ttk.Label(root, text="Beginning:").grid(row=0, column=0, padx=5, pady=5)
origin_entry = ttk.Entry(root, width=50)
origin_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(root, text="Destination:").grid(row=1, column=0, padx=5, pady=5)
destination_entry = ttk.Entry(root, width=50)
destination_entry.grid(row=1, column=1, padx=5, pady=5)

optimize_button = ttk.Button(root, text="Optimize Route", command=optimize_route)
optimize_button.grid(row=3, column=1, pady=5)

root.mainloop()
