# Malmo Homes

I need a supervised ML project to demo on my GitHub.

I am also interested in the housing prices in Malmo, Sweden.

I want to create a dataset of transactions that have taken place in Malmo, collecting information about final price (to predict) and predictor variables (location, type, size, amenities, etc).

I then want to train a ML model to predict price based on location. 

I want to make a nice interactive dashboard to investigate what features are important.


## Why is it interesting?

- House price prediction is fun - lots of examples - e.g. Ames Iowa housing dataset.
- In Malmo, fine geographic boundaries have a big impact on price, e.g. just this side of a road.
- Poor quality data is less of an issue with final prices

## Questions I would like to answer

- Is it better to treat house and apartments as separate prediction problems?
- How should I incorporate things like macro movements; strength of the kronor, interest rates, etc.
- How can I put those things into my prediction model as inputs that are also forecasts?

## Planning

### Components

Scraping: part 1 and continuous

Part 1 entails collecting information on completed sales from Hemnet. Have to be sure not to get IP blocked. 

CI is scraping e.g. each week to collect more housing prices to predict on and then retrain.
