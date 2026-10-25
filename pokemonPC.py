import requests
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()


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
        
    print(data["name"])
    # print(data["id"])
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

def labelObs(df,name,x,y):
  plt.annotate(
      name,
      (df.loc[df["Name"] == name.lower(), x].iloc[0],
       df.loc[df["Name"] == name.lower(), y].iloc[0])
  )


def lR(X,y):
  model = LinearRegression()
  
  model.fit(X, y)
  
  prediction = model.predict(X)
  
  plt.plot(X,prediction)
  
  #Print statistical analysis
  print("Slope:", model.coef_[0])
  print("Intercept:", model.intercept_)
  print("R²:", model.score(X, y))


def drawCanvas(fig):
  canvas = FigureCanvasTkAgg(fig, master = root)
  canvas_widget = canvas.get_tk_widget()
  canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
  canvas.draw()

def createPlot(df , var1,var2):
  #Setting scope
  plt.ylim(0, df[var1].max() * 1.1)
  plt.xlim(0, df[var2].max() * 1.1)

  #Scatterplot
  plt.scatter(df[var1], df[var2])

  #Labeling
  plt.xlabel(var1)
  plt.ylabel(var2)
  plt.title("Pokemon")

  labelObs(df , "pikachu", var1, var2)
  labelObs(df , "Mewtwo", var1, var2)
  labelObs(df , "Snorlax", var1, var2)
  labelObs(df , "Magikarp", var1, var2)


  #Linear Regression
  X = df[[var1]]
  y = df[var2]

  lR(X,y)
  fig = plt.gcf()
  drawCanvas(fig)


def createLine(df,var):
  fig, ax = plt.subplots(figsize=(8, 2))

  # Set limits and ticks for the number line dynamically
  padding = 2
  ax.set_xlim(min(df[var]) - padding, max(df[var]) + padding)
  ax.set_xticks(range(int(min(df[var]) - padding), int(max(df[var]) + padding + 1)))

  # Center the x-axis at y=0 and remove the y-axis
  ax.set_ylim(-1, 1)
  ax.get_yaxis().set_visible(False)
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['bottom'].set_visible(False)
  ax.spines['left'].set_visible(False)

  # Draw the horizontal number line
  ax.axhline(0, color='black', linewidth=1.5)

  # Plotting the list of df[var]
  y_values = [0] * len(df[var])
  ax.scatter(df[var], y_values, color='red', s=100, zorder=3, edgecolor='black')
  # Loop through the value and name columns together
  for x, label in zip(df[var], df["Name"]):
    ax.text(x, 0.15, str(label), color='red', weight='bold', ha='center')

  # Drawing canvas
  drawCanvas(fig)



root.title("My First Window")  
root.geometry("400x300")        

     

button = tk.Button(root,text = "createPlot", command = createPlot(df,"Attack","Special Attack"))
button.pack(pady=50)

button2 = tk.Button(root,text = "createList", command = createLine(df,"Speed"))
button2.pack(pady=50)

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


root.mainloop()