# UART Reader Manual

## How to use
### Re-define default settings
To redefine the default settings, please go to the `def database_initialization(db)` function, and change the values of the entries, be careful to not break the tuples, as the databaseV2 is a bit tricky in that aspect.

TODO : Add image

### Structure of the pickle file of the classifier model
Its structure is essentially just a dictionary containing the model and a bit more info for me to make it easy. It follows this convention :
```Python
pickled_data = {
    "model": sklearn.base.BaseEstimator, # The pre-trained classifier (fitted)
    "mel_len": 20, # Length of the mel-vector of the feature vector
    "mel_num": 20, # Number of mel-vectors in the feature vector
    "classes": ["gun", "chainsaw", "bird", "fire"],
    "mel_flat": False, # Do you need it to be N*Mx1 of size (np.ndarray[]) or NxM size (np.ndarray[np.ndarray[]]) ?
    "needs_hist": False, # Does it need more than 1 melvec ?
    "concat_hist": False, # Does the history need to be concatenated after each feature vector ?
    "num_hist": 1, # Number of historical ellements to use, this is a maximum, if there are not enough, then i can't give you more.
}
```
>NOTE : The model can also be a custom wrapper class, that allows to use the .predict(X) method, so that you can have any X depending on the parametters as defined above, and return a y that is the same length as the "classes" list.

### Instruction on use of the Mel Window (WARNING BUGS)
The mel window is the most patched up window in the whole program, as i had a hard time implementing it without a complete rewrite as i will explain further on in the document. This means that, if you want to use it with for example: a feature vector of 30x30 and a different model path, then you will first have to modify the parametters in the parametter window or initialization function for the database. Only then, can you open the Mel Window, and make the graphs work properly and not create errors or crash because of weird data formats.

## Internal Structure/Architecture of the `uart_readerV4`
TBD
## Problems, Choices and future evolution
### State of the pushed app
Because of time and mental health constraints (i have rewritten too many times all of this) in 2025, i have decided to release only the uart_readerV4, and not the V5 as it was already further along in development (front and backend almost finished). The V4 is quite flawed, and is based on a flawed implementation of the database (V2) that made it hard to use. I had to be crafty in a lot of places to allow for certain features, and because of the bad database design, it was almost impossible to do proper cleanup and support for multiple windows. So crashes can easilly happen because of the callbacks. 

### What i wanted to improve
After writing the V2 of the database, and using it in the V4 of the reader, i quickly realised that i was missing a lot of critical and tested implementations for each of the entries of the database (settings and stuff). This lead to the writing of the database V3. In this database, polymorphism was maximised, and a uniformity in the API was attempted, whilst trying to have as many type hints to know what to expect where. The only real issue i had with it is that there is apparently a problem with dark mode of Qt, making the text unreadable. In my optinion its perfectly capable, and and abstracts a lot of the complexities, whilst leaving a lot of functionality. But i will leave this to be fixed by whoever wants to use it. V3 was used to try to make the uart_readerV5, but this is still only the first brick of a skyscraper.

V4 of the database is a bit of a sketch version, as i tried to apply much more advanced concepts to it, and try to separate the API from the backed logick, while using python at its full potential (the code is probably still far off from peak python, and i also had to keep in mind to not use python 3.12+ features or very new stuff)

### If someone is up to it
I would recommend you to use the database V3 as its quite good, and has everything implemented and tested (even de serialization), whilst V4 still lacks quite a bit, but you do you. 

One thing to keep in mind, is that the hardest part of this whole thing was probably the MEL vector part, its still giving me nightmares because of the fact that feature vectors can be NxM with N not always equal to M. And making it update with the rest of the things, gave me a headache.

Good luck to you if you take on this challenge.
### Ramble on the architecture to aim for
The perfect architecture is a architecture that devides the application into 2 independent parts, that can mutate at their own rate. For instance, if you made a graph, you would want to have the UI read a array in memory, and update itself using that array. And when you have to change the data of the array, you can change it as fast as you want, as the GUI will just handle it. This separation allows you to make clear procedural generation of the GUI ellements at each update loop. It also allows you to change the underlying stuff, and re-render the whole ui with new parameters in a easier way. 

Another feature that is quite crititcal, but that is handled by the latests versions of the database (V3 and V4). Is the ability to use callbacks, as they allows you to not only update the UI when some value/array or anything else changes, but also allows you to add custom handlers for when you have to pre-process stuff. Though, one word of warning, the database is meant for non dynamic storage, as its quite heavy, if you wanted to make for example a update to a dynamically assembled list of plots on the UI, by changing a array, then you would have to create something else than the database. As the overhead would be a bit too big, and i also haven't updated it.

## Authors (Expand as needed)
- Group E 2024-2025
- (Future You ?)
