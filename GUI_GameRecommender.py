from tkinter import *
import pandas as pd
import datetime
import numpy as np


df=pd.read_csv("Video_Games_Sales_as_at_22_Dec_2016.csv")
data0=df.loc[:,["Name","Platform","Year_of_Release","Genre","Rating"]]
ind=data0.groupby(["Platform"])["Name"].count()

ind_pl=list(ind.index[ind>500])
data=data0.set_index("Platform").loc[ind_pl,:].reset_index()
data["Year_of_Release"]=data["Year_of_Release"].fillna("NaN.0")

indices=data.groupby("Genre").indices
options=list(indices.items())## transform it into list for indexing
options = [ list(x) for x in options]

Num=len(options)
weights_all = np.ones(Num)
print(weights_all)

data_full=data

choice=np.random.choice(Num,1)[0] ### global choice
print(choice)

gamma=0.1 ## set the speed parameter = 0.1

def update_prob(gamma,weight):
    return((1-gamma)*weight/sum(weight) + gamma/len(weight))

def recommend(ind_0,data):
    
    global options ## directly deal with global variable to remove the repeated one

    event_indices=options[ind_0][1]
    n=len(event_indices)
    choice_index=np.random.choice(n,1)[0]
    choice=event_indices[ choice_index ]
    event=data.iloc[choice,:]
    
    lbl1.configure(text=event["Name"])  ## update name
    lbl2.configure(text=event["Platform"]) ## update platform
    
    year=str(event["Year_of_Release"])
    lbl3.configure(text=year[:-2])  ## update release year

    lbl5.configure(text=event["Genre"])      ## update genre(recommend based on that)
    lbl6.configure(text=event["Rating"])     ## update rating
    
    print(len(options[ind_0][1]))
    options[ind_0][1] = np.delete(options[ind_0][1],choice_index)
    print(len(options[ind_0][1]))

#    lbl7.configure(text=event["link"])  ## update link
#    global web_url
#    web_url=event["link"]



def recommend_event(weights, options, data):
    
    Num=len(options)
    weights=weights/sum(weights) ## normalize to be summed as 1
    probability =update_prob(gamma, weights)
    choice=np.random.choice(Num, 1, p=probability)[0]
    
    #print("Recommend: "+ options[choice][0]) ## catrgory of recommendation
    recommend(choice,data)
    ##
    
    return(choice)

def update_weights(choice,weights,reward):
    probability =update_prob(gamma, weights)
    estimatedReward = 1.0 * reward / probability[choice]
    weights[choice] = weights[choice]*np.exp(estimatedReward * gamma / Num)
    return(weights)


#def callback(event):
#    global web_url
#    webbrowser.open_new(web_url)


key=list(indices.keys())
print(key)

window = Tk()

window.title("Game Recommender")

window.geometry('650x500')

### construct the panel

lbl = Label(window, text="Recommended Game:")
lbl.place(relx=0.5, rely=0.1, anchor=CENTER)
lbl.config(font=("Courier", 24))

lbl1 = Label(window, text="")
lbl1.place(relx=0.5, rely=0.2, anchor=CENTER)
lbl1.config(font=("Times", 20))

lbl0 = Label(window, text="Platform and release-year")
lbl0.place(relx=0.5, rely=0.4, anchor=CENTER)
lbl0.config(font=("Courier", 24))

lbl2 = Label(window, text="")
lbl2.place(relx=0.2, rely=0.5, anchor=CENTER)

lbl3 = Label(window, text="")
lbl3.place(relx=0.8, rely=0.5, anchor=CENTER)

lbl4 = Label(window, text="Genre and rating")
lbl4.place(relx=0.5, rely=0.6, anchor=CENTER)
lbl4.config(font=("Courier", 24))

lbl5 = Label(window, text="")
lbl5.place(relx=0.2, rely=0.7, anchor=CENTER)

lbl6 = Label(window, text="")
lbl6.place(relx=0.8, rely=0.7, anchor=CENTER)

#lbl7 = Label(window, text="Link to the event(please click)",fg="blue", cursor="hand2")
#lbl7.place(relx=0.5, rely=0.3, anchor=CENTER)
#lbl7.bind("<Button-1>",callback)

recommend(choice,data)



def click_like():
    global choice
    global key
    print("Like: "+ key[choice])

    global weights_all
    ### update weights first and then flush the output
    theReward=1
    

    weight_new = update_weights(choice,weights_all,theReward)
    ## update the global weights and probability
    weights_all = weight_new
    choice=recommend_event(weights_all,options,data_full)
    print(weights_all)

def click_hate():
    
    global key
    global choice
    print("Dislike: "+key[choice])

    
    global weights_all
    ### update weights first and then flush the output
    theReward=-1

    weight_new = update_weights(choice,weights_all,theReward)
    ## update the global weights and probability
    weights_all = weight_new
    choice=recommend_event(weights_all,options,data_full)
    print(weights_all)



btn1 = Button(window, text="Like!", command=click_like)
btn2 = Button(window, text="Dislike!", command=click_hate)
btn_quit = Button(window, text='Quit', command=window.quit)

btn1.place(relx=0.1, rely=0.9, anchor=CENTER)
btn2.place(relx=0.9, rely=0.9, anchor=CENTER)
btn_quit.place(relx=0.5, rely=0.9, anchor=CENTER)

window.mainloop()
