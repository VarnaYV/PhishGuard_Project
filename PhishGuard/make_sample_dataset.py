"""Generates dataset/sample_dataset.csv: SYNTHETIC, fictional URLs for demonstration only."""
import random, csv
random.seed(7)
legit_hosts = ["www.google.com","github.com","www.wikipedia.org","docs.python.org","stackoverflow.com","www.bbc.co.uk","www.microsoft.com",
 "www.amazon.in","www.coursera.org","news.ycombinator.com","www.nytimes.com","pypi.org","www.mozilla.org","www.khanacademy.org","www.who.int"]
legit_paths = ["","/","/about","/docs/index.html","/search?q=python","/products/item-102","/wiki/Machine_learning","/blog/2024/05/post","/help/contact","/en/latest/tutorial"]
brands = ["paypal","amazon","google","microsoft","apple","netflix","sbi","hdfc","instagram","facebook"]
kws = ["login","verify","secure","account","update","confirm","signin","banking","wallet","password"]
tlds = ["xyz","top","click","link","work","tk","ml","ga","cf","gq","info","com"]
rows = set()
while len(rows) < 300:
    rows.add((random.choice(["https://","https://","http://"]) + random.choice(legit_hosts) + random.choice(legit_paths) + (f"?id={random.randint(1,999)}" if random.random()<.3 else ""), 0))
while len(rows) < 600:
    b,k1,k2,t = random.choice(brands),random.choice(kws),random.choice(kws),random.choice(tlds)
    host = random.choice([f"{k1}-{b}-{k2}.{t}", f"{b}.{k1}.{k2}.example-{random.randint(10,99)}.{t}", f"{k1}-{k2}-{b}{random.randint(1,999)}.{t}",
                          f"{random.randint(11,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"])
    rows.add((random.choice(["http://","http://","https://"]) + host + f"/{k1}/{k2}" + random.choice(["","/index.php",f"?session={random.randint(10**5,10**6)}&user=x"]), 1))
with open("dataset/sample_dataset.csv","w",newline="") as f:
    w = csv.writer(f); w.writerow(["url","label"]); w.writerows(sorted(rows, key=lambda r: random.random()))
