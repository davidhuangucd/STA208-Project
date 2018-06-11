from tkinter import *
import pandas as pd
import datetime
import numpy as np
from datetime import timedelta
import geocoder
import webbrowser

g = geocoder.ip('me')

today = datetime.date.today()
endDate = today + timedelta(days=5)
today_str = today.strftime('%Y-%m-%dT%H:%M:%SZ')
endDate_str = endDate.strftime('%Y-%m-%dT%H:%M:%SZ')

mykey="Abiv3plK1RopGuqNsk8eduAiyvhTVPdI"
import ticketpy
tm_client = ticketpy.ApiClient(mykey)

pages = tm_client.events.find(
                              latlong=g.latlng,
                              state_code='CA',
                              start_date_time=today_str,
                              end_date_time=endDate_str,
                              )

def extract_cont(x,label):
    if(label in x.keys()):
        return(x[label])
    else:
        return(None)
def extract_information(event):
    
    event_content=event.json## transfrom event to json
    
    ## general information of this event
    name=extract_cont(event_content,"name")
    url=extract_cont(event_content,"url")
    image=extract_cont(event_content["images"][0],"url")
    classifcation =extract_cont(event_content,"classifications")
    if( classifcation ):
        classifcation=classifcation[0]
    else:
        return(None)
    genre=extract_cont(classifcation,"genre")
    if(genre):
        genre=genre["name"]
    else:
        genre=None
    category=extract_cont(classifcation,"segment")

    if(category):
        category=category["name"]
    else:
        category=None
## extract location

    venue=event_content['_embedded']["venues"][0]
    lat=venue["location"]['latitude']
    lon=venue["location"]['longitude']
    city=venue["city"]['name']

    place=venue['name']
    return({ "name":name,"link":url,"image":image,"genre":genre,"category":category,
       "latitude":lat,'longtitude':lon,"city":city,"place":place})

r=[]
for page in pages:
    for event in page:
        r.append(event)

r2=[]
for event in r:
    t=extract_information(event)
    if(t!=None):
        r2.append(t)
data=pd.DataFrame(r2)
data=data.loc[data["category"]!="Undefined"] ## remove undefined category


indices=data.groupby("category").indices

options=list(indices.items())## transform it into list for indexing

Num=len(indices)
weights_all = np.ones(Num)
print(weights_all)

data_full=data

choice=np.random.choice(len(options),1)[0] ### global choice
print(choice)

gamma=0.1 ## set the speed parameter = 0.1

def update_prob(gamma,weight):
    return((1-gamma)*weight/sum(weight) + gamma/len(weight))

def recommend(event0,data):

    event_indices=event0[1]
    n=len(event_indices)
    choice=event_indices[np.random.choice(n,1)[0]]
    event=data.iloc[choice,:]
    
    lbl1.configure(text=event["name"])  ## update name
    lbl2.configure(text=event["place"]) ## update place
    lbl3.configure(text=event["city"])  ## update city

    lbl5.configure(text=event["category"])  ## update category
    lbl6.configure(text=event["genre"])     ## update genre

#lbl7.configure(text=event["link"])  ## update link
    global web_url
    web_url=event["link"]



def recommend_event(weights, options, data):
    
    Num=len(options)
    weights=weights/sum(weights) ## normalize to be summed as 1
    probability =update_prob(gamma, weights)
    choice=np.random.choice(Num, 1, p=probability)[0]
    #print("Recommend: "+ options[choice][0]) ## catrgory of recommendation
    recommend(options[choice],data)
    return(choice)

def update_weights(choice,weights,reward):
    probability =update_prob(gamma, weights)
    estimatedReward = 1.0 * reward / probability[choice]
    weights[choice] = weights[choice]*np.exp(estimatedReward * gamma / Num)
    return(weights)

def callback(event):
    global web_url
    webbrowser.open_new(web_url)


key=list(indices.keys())

window = Tk()

window.title("Event Recommender")

window.geometry('650x500')

lbl = Label(window, text="Recommended event:")
lbl.place(relx=0.5, rely=0.1, anchor=CENTER)
lbl.config(font=("Courier", 24))


lbl1 = Label(window, text="")
lbl1.place(relx=0.5, rely=0.2, anchor=CENTER)
lbl1.config(font=("Times", 20))

lbl0 = Label(window, text="Location")
lbl0.place(relx=0.5, rely=0.4, anchor=CENTER)
lbl0.config(font=("Courier", 24))

lbl2 = Label(window, text="")
lbl2.place(relx=0.2, rely=0.5, anchor=CENTER)

lbl3 = Label(window, text="")
lbl3.place(relx=0.8, rely=0.5, anchor=CENTER)

lbl4 = Label(window, text="Category and genre")
lbl4.place(relx=0.5, rely=0.6, anchor=CENTER)
lbl4.config(font=("Courier", 24))

lbl5 = Label(window, text="")
lbl5.place(relx=0.2, rely=0.7, anchor=CENTER)

lbl6 = Label(window, text="")
lbl6.place(relx=0.8, rely=0.7, anchor=CENTER)

lbl7 = Label(window, text="Link to the event(please click)",fg="blue", cursor="hand2")
lbl7.place(relx=0.5, rely=0.3, anchor=CENTER)
lbl7.bind("<Button-1>",callback)

recommend(options[choice],data)



def click_like():
    global choice
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
