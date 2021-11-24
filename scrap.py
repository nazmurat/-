from flask_sqlalchemy import SQLAlchemy
from flask import Flask , render_template, redirect , url_for
from flask import request
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Register125@localhost/FinalPython'
db = SQLAlchemy(app)

class Coin(db.Model):
    __tablename__ = 'coin'
    id = db.Column('id',db.Integer,primary_key=True)
    coin_name = db.Column('coin_name', db.Unicode)
    blogs = db.Column('blogs',db.Unicode)
    summarized_blogs = db.Column('summarized_blogs',db.Unicode)

    def __init__(self,coin_name,blogs,summarized_blogs):
        self.coin_name = coin_name
        self.blogs = blogs
        self.summarized_blogs = summarized_blogs





def scrappper(coin4):

    r = requests.get('https://cryptonews.com/news/'+coin4+'-news/')
    soup = BeautifulSoup(r.text, 'html.parser')

    for div in soup.find_all("div", {'class':'article__badge article__badge--md mb-10 pt-10'}): 
        div.decompose()

    link = soup.find_all('div',class_='col-12 col-md-7 column-45__right d-flex flex-column justify-content-center')
    
    links = []
    
    for ssilka in link:
        links.append(ssilka.find('a').attrs['href'])
    
    news = []
    
    for news_url in links:
        html_team = requests.get('https://cryptonews.com/'+news_url).text
        soup_team = BeautifulSoup(html_team,'html.parser')
        
        for div1 in soup_team.find_all("div", {'class':'left-side'}): 
            div1.decompose()

        paragraphs = soup_team.find_all('p',limit=5)
        text = [result.text for result in paragraphs]
        ARTICLE = ' '.join(text)
        news.append(ARTICLE)
    
    return news

def summarizer(blogs):
    sumsum = []
    summarizer = pipeline("summarization")
    res = summarizer(blogs, max_length=120, min_length=30, do_sample=False)
    
    for r in res:
        sumsum.append(r['summary_text']) 

    return sumsum






@app.route('/',methods=["GET"])    
def coin_index():
    return render_template("coin.html")
        

@app.route('/',methods=["POST"])
def coin():
    coin = request.form['coin']
    
    if not coin:
        return redirect(url_for('coin_index'))

    data =Coin.query.filter_by(coin_name=coin).first()
    if data:
        return redirect(url_for('crypto',crypto=coin))
    blogs=scrappper(coin)
    summary=summarizer(blogs)
    coins = Coin(coin_name=coin,blogs=blogs,summarized_blogs=summary)
    db.session.add(coins)
    db.session.commit()
    return redirect(url_for('crypto',crypto=coins.coin_name))

@app.route('/<crypto>',methods=["POST","GET"])
def crypto(crypto):
    

    if request.method == "POST":
        c = request.form['coin']
        if not c:
            return redirect(url_for('coin_index'))
        
        data =Coin.query.filter_by(coin_name=c).first()
        
        if data:
            new = str(data.blogs).replace('"', " ").replace("{"," ").replace("}"," ")
            sumsumsum = str(data.summarized_blogs).replace('"', " ").replace("{"," ").replace("}"," ")
            s = sumsumsum.split(' , ')
            l = new.split(' , ')
            return render_template("crypto.html",rev=zip(s, l), title = data.coin_name)
      
        blogs=scrappper(c)

        summary=summarizer(blogs)

        coin = Coin(coin_name=c,blogs=blogs,summarized_blogs=summary)
        db.session.add(coin)
        db.session.commit()
        return redirect(url_for('crypto',crypto=c))
    
    
    coins = Coin.query.filter_by(coin_name = crypto).first()
    new = str(coins.blogs).replace('"', " ").replace("{"," ").replace("}"," ")
    sumsumsum = str(coins.summarized_blogs).replace('"', " ").replace("{"," ").replace("}"," ")
    s = sumsumsum.split(' , ')
    l = new.split(' , ')
    return render_template("crypto.html",rev=zip(s,l), title = coins.coin_name)



if __name__ == '__main__':  
    app.run(debug=True)
