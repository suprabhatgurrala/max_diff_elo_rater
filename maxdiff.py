import os

import pandas as pd


ELO_RATINGS_FILE = "elo_ratings.csv"


class MaxDiffRater:

    def __init__(self, elo_ratings=None, k_factor=32):
        if elo_ratings is None:
            if os.path.isfile(ELO_RATINGS_FILE):
                self.load_elo_ratings()
            else:
                self.initialize_items()
        else:
            self.elo_ratings = elo_ratings
        self.k_factor = k_factor
        

    def initialize_items(self):
        self.elo_ratings = pd.read_csv("items.csv", names=["items"])
        self.elo_ratings["elo"] = 1500
        self.elo_ratings["matches"] = 0
        self.store_elo_ratings()


    def store_elo_ratings(self):
        self.elo_ratings.to_csv("elo_ratings.csv", index_label="id")


    def load_elo_ratings(self):
        self.elo_ratings = pd.read_csv("elo_ratings.csv", index_col="id")


    def update_elo(self, elo_ratings, winner, loser):
        print(f"Updating elo for {winner} over {loser}")
        if winner == loser:
            return
        
        a = elo_ratings.loc[winner]["elo"]
        b = elo_ratings.loc[loser]["elo"]
        
        expected = 1 / (1 + 10**((b - a) / 400))
        
        rating_change = k_factor * (1 - expected)
        
        elo_ratings.at[winner, "elo"] += rating_change
        elo_ratings.at[loser, "elo"] -= rating_change
        
        elo_ratings.at[winner, "matches"] += 1
        elo_ratings.at[loser, "matches"] += 1
        
        store_elo_ratings(elo_ratings)


    def get_sample(self, bucket_size=5):
        least_sample = self.elo_ratings.nsmallest(bucket_size, "matches", keep="all")
        
        if least_sample.shape[0] > bucket_size:
            least_sample = least_sample.sample(bucket_size)
        
        return least_sample

    def driver(self):
        bucket_size = 5
        print(f"You will be given {bucket_size} items. You will be asked to identify the best and worst item in each bucket. Enter -1 to exit.")
        input_val = 0
        while input_val != -1:    
            contenders = get_sample(bucket_size)
            
            display(contenders)
            print("Enter the index of the best item in this list: ")
            best = int(input())

            if best == -1:
                break
            elif best not in contenders.index:
                print("Entered index was not one of the options.")
            
                
            print(f"Marking movie {best} as best.")
            
            print("Enter the index of the worst item in this list:")
            worst = int(input())
            
            if worst == -1:
                break
                
            print(f"Marking movie {worst} as worst.")
            
            for i in contenders.index:
                if i != best:
                    update_elo(best, i)
                if (i != worst) and (i != best):
                    update_elo(i, worst)
            elo_ratings.to_csv("elo_ratings.csv", index_label="id")
            elo_ratings.sort_values("elo", ascending=False)