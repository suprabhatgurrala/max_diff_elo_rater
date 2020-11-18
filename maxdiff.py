import os

import pandas as pd


ELO_RATINGS_FILE = "elo_ratings.csv"
HISTORY_FILE = "history.tsv"


class MaxDiffRater:

    def __init__(self, start_k_factor=40, k_factor_decay=0.99):
        """
        Initialize a MaxDiffRater
        :param start_k_factor: Sets the max K-factor for an Elo update on a new item
        :param k_factor_decay: The amount to decay the k_factor for each update on an item. Set to 1 to disable k_factor decay
        """    
        self.load_elo_ratings()
        self.load_history()
        
        self.start_k_factor = start_k_factor
        self.k_factor_decay = k_factor_decay
        
    
    def store_elo_ratings(self):
        """Save the elo ratings to disk"""
        self.elo_ratings.to_csv(ELO_RATINGS_FILE, index_label="id")

    def load_elo_ratings(self):
        """Read elo ratings from disk"""
        # Load a previously used Elo ratings file from disk
        if os.path.isfile(ELO_RATINGS_FILE):
            self.elo_ratings = pd.read_csv(ELO_RATINGS_FILE, index_col="id")
        else:
            # Create Elo ratings from a list of items
            self.elo_ratings = pd.read_csv("items.csv", names=["items"])
            self.elo_ratings["elo"] = 1500
            self.elo_ratings["matches"] = 0
            self.store_elo_ratings()
        

    def load_history(self):
        """Read history from disk"""
        if os.path.isfile(HISTORY_FILE):
            self.history = pd.read_csv(HISTORY_FILE, index_col="answer_id", sep="\t")
        else:
            self.history = pd.DataFrame(columns=["best", "worst", "group"])

    def store_history(self):
        """Save history to disk"""
        self.history.to_csv(HISTORY_FILE, index_label="answer_id", sep="\t")

    def update_elo(self, winner, loser):
        """
        Calculate the Elo updates for a single match
        :param winner: id of the winning item
        :param loser: id of the losing item
        """
        if winner == loser:
            # Winners and losers can't be the same
            return
            
        # Get elo ratings for each item
        a = self.elo_ratings.loc[winner]["elo"]
        b = self.elo_ratings.loc[loser]["elo"]

        a_matches = self.elo_ratings.loc[winner]["matches"]
        b_matches = self.elo_ratings.loc[winner]["matches"]
        
        # Calculate expected win probability for winner
        expected = 1 / (1 + 10**((b - a) / 400))
        
        a_rating_change = (self.start_k_factor * self.k_factor_decay**a_matches) * (1 - expected)
        b_rating_change = (self.start_k_factor * self.k_factor_decay**b_matches) * (1 - expected)
        
        # Make rating changes
        self.elo_ratings.at[winner, "elo"] += a_rating_change
        self.elo_ratings.at[loser, "elo"] -= b_rating_change
        
        # Increment number of matches
        self.elo_ratings.at[winner, "matches"] += 1
        self.elo_ratings.at[loser, "matches"] += 1
    
    def submit_results(self, sample_ids, best, worst):
        """
        Perform Elo updates for an answer from a MaxDiff sample.
        This code is designed to handle the data that comes from a POST request of the HTML form.
        :param sample_ids: the list of ids that were presented in the MaxDiff sample
        :param best: the id of the best item
        :param worst: the id of the worst item
        """
        best = int(best)
        worst = int(worst)

        sample_id_list = []

        for i in sample_ids:
            i = int(i.replace("/", ""))

            if i != best:
                # We can infer that the best would "win" against the other items in the sample
                self.update_elo(best, i)
            if (i != worst) and (i != best):
                # We can infer that the other items in the sample would "win" against the worst    
                self.update_elo(i, worst)
            sample_id_list.append(i)

        self.history = self.history.append({
            "best": best,
            "worst": worst,
            "group": sample_id_list
            },
            ignore_index=True
        )
        self.store_history()
        
        # Store our changes to disk
        self.store_elo_ratings()

    def get_sample(self, bucket_size=5):
        """
        Get a sample of items, with a bias towards items that have been picked less frequently.
        :param bucket_size: the number of items to get per sample
        """
        # Get all items that have been picked the least
        i = 1
        least_sample = self.elo_ratings.nsmallest(i, "matches", keep="all")

        # Continue to get the least picked items if there aren't enough
        while (least_sample.shape[0] < bucket_size) and (i < bucket_size):
            i += 1
            least_sample = self.elo_ratings.nsmallest(i, "matches", keep="all")
        
        # Take a sample if there are more items than the bucket size
        if least_sample.shape[0] > bucket_size:
            least_sample = least_sample.sample(bucket_size)
        
        return least_sample
