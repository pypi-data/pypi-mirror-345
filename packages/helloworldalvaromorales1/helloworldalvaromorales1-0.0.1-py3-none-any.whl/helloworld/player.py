""" 
This is the documentation of the player module.
"""

class Player:
    """
    This is a class and the documentation of the Player class.
    """

    def play(self, song):
        """
        This is the documentation of the play method.
        And plays the given song.

        Args:
        song (str): The name of the song to play.

        Returns:
        int: 1 if the song is played successfully, 0 otherwise.
        """
        print(f"Playing {song}")
        return 1

    def stop(self):
        print("Stopping the player")