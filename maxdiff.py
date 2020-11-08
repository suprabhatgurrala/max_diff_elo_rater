import os

import pandas as pd


ELO_RATINGS_FILE = "elo_ratings.csv"


class MaxDiffRater:

    def __init__(self, k_factor=32):
        """
        Initialize a MaxDiffRater
        :param k_factor: Sets the K-factor for the Elo update
        """
        # Load a previously used Elo ratings file from disk
        if os.path.isfile(ELO_RATINGS_FILE):
            self.load_elo_ratings()
        else:
            # Create Elo ratings from a list of items
            self.initialize_items()
        
        self.k_factor = k_factor
        
    def initialize_items(self):
        """Read list of items from file and initialize the elo ratings"""
        self.elo_ratings = pd.read_csv("items.csv", names=["items"])
        self.elo_ratings["elo"] = 1500
        self.elo_ratings["matches"] = 0
        self.store_elo_ratings()

    def store_elo_ratings(self):
        """Save the elo ratings to disk"""
        self.elo_ratings.to_csv("elo_ratings.csv", index_label="id")

    def load_elo_ratings(self):
        """Read elo ratings from disk"""
        self.elo_ratings = pd.read_csv("elo_ratings.csv", index_col="id")

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
        
        # Calculate expected win probability for winner
        expected = 1 / (1 + 10**((b - a) / 400))
        
        rating_change = self.k_factor * (1 - expected)
        
        # Make rating changes
        self.elo_ratings.at[winner, "elo"] += rating_change
        self.elo_ratings.at[loser, "elo"] -= rating_change
        
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

        for i in sample_ids:
            i = int(i.replace("/", ""))

            if i != best:
                # We can infer that the best would "win" against the other items in the sample
                self.update_elo(best, i)
            if (i != worst) and (i != best):
                # We can infer that the other items in the sample would "win" against the worst    
                self.update_elo(i, worst)
        
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
