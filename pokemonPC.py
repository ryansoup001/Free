import requests
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import mplcursors

root = tk.Tk()

canvas = None

REGION = "Kanto"
REGION_RANGE = (0,0) 

if (REGION == "Kanto"):
  REGION_RANGE = (1,152)
elif (REGION == "Sinnoh"):
  REGION_RANGE = (152,151)
elif (REGION == "Hoenn"):
  REGION_RANGE = (1,151)

def get_pokemon(pokemon_ID):
  if (not pokemon_ID.isnumeric()):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_ID.lower()}"
  else:
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_ID}"

  response = requests.get(url)

  if response.status_code == 200:
    #REQUEST SUCCESSFUL
    data = response.json()
    pokemon = {
      "Name": data["name"],
      "ID": data["id"],
      "Height": data["height"],
      "Weight": data["weight"],
      "Type": data["types"],
      "Abilities": data["abilities"],
      "Stats": data["stats"]
      
    }
    # #untabelizing stats
    # df["HP"] = df["Stats"].apply(lambda stats: stats[0]["base_stat"])
    # df["Attack"] = df["Stats"].apply(lambda stats: stats[1]["base_stat"])
    # df["Special Attack"] = df["Stats"].apply(lambda stats: stats[2]["base_stat"])
    # df["Defense"] = df["Stats"].apply(lambda stats: stats[3]["base_stat"])
    # df["Special Defense"] = df["Stats"].apply(lambda stats: stats[4]["base_stat"])
    # df["Speed"] = df["Stats"].apply(lambda stats: stats[5]["base_stat"])
        
    
    # print(data["id"])
    print(data["name"])
    # print(data["types"][0]["type"]["name"])
    # for i in data["abilities"]: 
    #   if (not i["is_hidden"]):
    #     print(i["ability"]["name"])
    #print("\n")
    return pokemon
  elif response.status_code == 404:
    print("Error 404:" + pokemon_ID + "not found")
  else:
    print("Failed to fetch")


#KANTO REGION
pokemon_data = []
for i in range(*REGION_RANGE):
  pokemon_data.append(get_pokemon(str(i)))

df = pd.DataFrame(pokemon_data)

# giving individual stats tables in DataFrame
df["HP"] = df["Stats"].apply(lambda stats: stats[0]["base_stat"])
df["Attack"] = df["Stats"].apply(lambda stats: stats[1]["base_stat"])
df["Special Attack"] = df["Stats"].apply(lambda stats: stats[2]["base_stat"])
df["Defense"] = df["Stats"].apply(lambda stats: stats[3]["base_stat"])
df["Special Defense"] = df["Stats"].apply(lambda stats: stats[4]["base_stat"])
df["Speed"] = df["Stats"].apply(lambda stats: stats[5]["base_stat"])

def labelObs(df, name, x, y, ax):
    pokemon = df.loc[df["Name"] == name.lower()]

    if not pokemon.empty:
        row = pokemon.iloc[0]
        ax.annotate(name, (row[x], row[y]))


def lR(X, y, ax):
  model = LinearRegression()
  model.fit(X, y)

  # Sort X so the regression line is drawn correctly
  X_sorted = X.sort_values(by=X.columns[0])
  prediction = model.predict(X_sorted)

  ax.plot(X_sorted.iloc[:, 0], prediction, color="red")

  return model

# K-Means [UNSUPERVISED LEARNING]
def Knn(X,ax,n_clusters=3):
  # 1. K-Means heavily relies on distance, so you must scale the features 
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 2. Initialize and fit K-Means (Notice: NO 'y' is passed here!)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    # 3. Get the calculated cluster centers
    centers = kmeans.cluster_centers_
    scatter = ax.scatter(
        X.iloc[:, 0],  # Feature 1 (X-axis dropdown selection)
        X.iloc[:, 1],  # Feature 2 (Y-axis dropdown selection)
        c=cluster_labels, 
        cmap='viridis', 
        edgecolors='k', 
        alpha=0.8
    )
    print("Clustering for k-means" , n_clusters)
    return scatter
   


def drawCanvas(fig,master):
    global canvas

    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    canvas.draw()

def clear_canvas():
  global canvas

  if canvas is not None:
      canvas.get_tk_widget().destroy()
      canvas = None

  plt.close("all")
   

def createPlot(df, var1, var2 , master, algo):
    clear_canvas()

    sc = None
    fig, ax = plt.subplots(figsize=(6, 4))

    X = df[[var1]]
    y = df[var2]

    if algo == "Linear":
          # model = lR(X,y,ax)
          lR(X, y, ax)
    elif algo == "KNN":
          X = df[[var1, var2]]
          sc = Knn(X,ax) 
    else:
      # Scatterplot
      sc = ax.scatter(df[var1], df[var2])

    # Labels and title
    ax.set_xlabel(var1)
    ax.set_ylabel(var2)
    ax.set_title("Pokemon")

    # Axis limits
    ax.set_ylim(0, df[var1].max() * 1.1)
    ax.set_xlim(0, df[var2].max() * 1.1)


    cursor = mplcursors.cursor(sc, hover=True)

    # Label selected Pokémon
    # for name in ["Pikachu", "Mewtwo", "Snorlax", "Magikarp"]:
    #   labelObs(df, name, var1, var2, ax)
    if 'Name' in df.columns:
      @cursor.connect("add")
      def on_add(sel):
          # Fetch index of the hovered point
          idx = sel.index
          pokemon_name = df.iloc[idx]['Name']
          # Format the text box layout
          sel.annotation.set_text(f"{pokemon_name}\n{var1}: {sel.target[0]}\n{var2}: {sel.target[1]}")

    # Linear regression
      
      
      #Print statistical analysis
      # print("Slope:", model.coef_[0])
      # print("Intercept:", model.intercept_)
      # print("R²:", model.score(X, y))
        
    fig.tight_layout()
    drawCanvas(fig, master)


def createLine(df, var, master, algo):
  clear_canvas()

  sc = None
  fig, ax = plt.subplots(figsize=(8, 4))

  X = df[["ID"]]
  y = df[var]
  if (algo == "Linear"):
    lR(X,y,ax)
  elif algo == "KNN":
    X = df[["ID",var]]
    sc = Knn(X,ax)
  else:
    sc = ax.scatter(df["ID"], df[var])

  ax.set_xlabel("ID")
  ax.set_ylabel(var)
  ax.set_title("Pokemon 1D")
    
  cursor = mplcursors.cursor(sc, hover=True)

  if 'Name' in df.columns:
    @cursor.connect("add")
    def on_add(sel):
      # Fetch index of the hovered point
      idx = sel.index
      pokemon_name = df.iloc[idx]['Name']
      # Format the text box layout
      sel.annotation.set_text(f"{pokemon_name}\n{"ID"}: {sel.target[0]}\n{var}: {sel.target[1]}")

    
    
    # for _, row in df.iterrows():
    #     if random.randint(1, 4) == 4:
    #         labelObs(df, row["Name"], "ID", var, ax)

    fig.tight_layout()
    drawCanvas(fig, master)



root.title("My First Window")  
root.geometry("400x300")        
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

page1 = ttk.Frame(notebook)


page1_options = ["HP","Attack","Special Attack", "Defense", "Special Defense", "Speed"]

combo1 = ttk.Combobox(page1, values = page1_options, state = "read-only")
combo1.set("Choose First Stat")
combo1.pack(pady=50)


combo2 = ttk.Combobox(page1, values = page1_options, state = "read-only")
combo2.set("Choose Second Stat")
combo2.pack(pady=50)

button = tk.Button(page1,text = "createPlot", command=lambda: createPlot(df,combo1.get(),combo2.get(), page1, "Linear"))
button.pack(pady=50)

button2 = tk.Button(page1,text = "createList", command=lambda: createLine(df,combo1.get(), page1, "Linear"))
button2.pack(pady=50)

# print("Available columns:", df.columns.tolist()) 


#Page 2[KNN/ Pokemon Similarity Calculator]

page2 = ttk.Frame(notebook)

page2_options = ["HP","Attack","Special Attack", "Defense", "Special Defense", "Speed", "Active"]

combo3 = ttk.Combobox(page2, values = page2_options, state = "read-only")
combo3.set("Choose First Stat")
combo3.pack(pady=50)

combo4 = ttk.Combobox(page2, values = page2_options, state = "read-only")
combo4.set("Choose Second Stat")
combo4.pack(pady=50)

button3 = tk.Button(page2,text = "createPlot", command=lambda: createPlot(df,combo3.get(),combo4.get(), page2, "KNN"))
button3.pack(pady=50)

button4 = tk.Button(page2,text = "createList", command=lambda: createLine(df,combo3.get(), page2, "KNN"))
button4.pack(pady=50)
#extra functions

# def predSpeed(df):
#   #Setting up variables
#   ratio = df["Weight"] / df["Height"]
#   df["height_weight_ratio"] = ratio
#   X = X = ratio.to_numpy().reshape(-1, 1)
#   y = df["Speed"]

#   #label Pikachu
#   labelObs(df,"Pikachu","height_weight_ratio", "Speed")
  
#   #Plot ratio of the Height and Weight to descirbe Speed
#   plt.scatter(ratio, df["Speed"])

notebook.add(page1, text="Linear Regression/Ratio")
notebook.add(page2, text="Pokemon Similarity Calculator/KNN")

root.mainloop()