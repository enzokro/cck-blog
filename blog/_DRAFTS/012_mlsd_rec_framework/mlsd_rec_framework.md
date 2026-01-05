# An ML System Design Framework for Recommender Systems

# Introduction  

ML System Design (MLSD) Interviews are one of the most ambiguous parts of modern ML Interviews. Different companies look for vastly different things in their MLSD screenings, and the interview itself depends on whether the role focuses on Research, Infrastructure, or Applications. MLSD interviews are not at all like Coding Screenings that mostly operate around LeetCode-like formats. 

The most common (or at least well-defined) of the interviews is the Applied ML System interview. Candidates are given an overly broad goal such as "Design the YouTube home page," "Design the TikTok For You Page," "Design an Ad Ranker for Newsfeed," or "Design a system to find Marketplace listings with restricted content," "Design a People You May Know / Follower Recommendations for Instagram / Facebook / Threads". 

These broad tasks fall under three categories: 
- Harmful Content Detection
- Recommender Systems
- NLP Classification  

This post will focus on Recommender Systems and Harmful Content Detection. However, we won't get into the specifics of different recommendations or kinds of harmful content. Instead, we will spell out the broad patterns that rule each task. This lets us build up a framework that can be applied to any specific problem we come across. 

# Recommendation Systems 

The history of recommender systems is vast and storied. They underpin the ad economy of the internet that has fundamentally shaped (for better and worse) our modern information ecosystem and, by extension, society. 

The ML community has been incredibly open and generous when it comes to sharing their discoveries and techniques. Recommender systems are the one area where this is less true compared to vision, speech, and tabular ML. And this is very understandable - companies toil long and hard to raise their golden recommender geese and don't want to give away their advantages. Still, thanks to the incredibly kind and valuable tradition of publishing and sharing, we have a fairly good idea of what State of the Art recommender systems look like in the wild. 

## Framing the Business Objective 

The high-level task we are given to "Design a system that..." is only meant as a setup. The business has very clear goals in mind when they deploy our final ML System. This means we must first translate the design task into the actual, underlying need that the business cares about. 

The interviewer is seeing if we can translate a broad, ambitious, and nebulous goal into a concrete business outcome that would actually drive day-to-day operations. This is one of the first things we are evaluated on. 

It is also a good place for senior candidates to stand out. Regardless of the specific system we are given, the main goal will be some version of "increase engagement." However, optimizing only for this outcome is a great way to collapse into degenerate, undesirable states. Machine Learning systems are, for all of their recent progress and power, inherently lazy and follow the path of least resistance.

For example, if we only optimize for "remove illegal ads" then the degenerate outcome is to simply block all ads. In that case no illegal ones will ever get through. If we only optimize for "increase watchtime," then the best thing to do is recommend low-quality videos that mindlessly but frequently engages users. If we only optimize CTR, then we end up suggesting clickbait titles and thumbnails that users click on but immediately realize are misleading or trash and leave. All systems face a similar, degenerate version of only optimizing for their single, obvious metric. 

Instead, we must consider long-term platform health and all stakeholders (users, creators, advertisers) from the get-go. This guides our main business objective: maximize the obvious metric, with an eye to long-term platform health that accomplishes the following:  
- Maximizes positive user experiences 
- Maximizes positive experiences for creators / advertisers
-- Do not penalize new, smaller creators and advertisers, or overly favor large creators and advertisers

This framing shows both seniority and stopgaps many potential gotcha questions down the road. It also sets you up nicely to talk about org-level considerations as you develop the system.  

## Framing the ML Objective  

In this case, the ML objective becomes clear from the long-term business object: given a user and their context, rank a series of items by the probability that they will both increase our metric *and* lead to long-term platform health. 

## The Universal Recommendation Entities 

Every recommender system is built around four key entities:  
- Users  
- Items  
- User-Item Engagements
- User Behavioral and/or Contextual Features

Users and Items tend to be static. We can extract and cache their embeddings to massively reduce the compute cost of our overall pipeline, helping to meet the strict latency requirements. We will still need to re-train or re-extract them periodically for good measure, or when certain triggers are fired. These entities are like the fixed bedrock from which platform behavior springs forth.

Engagements and Behavioral features are more dynamic and need to be constantly updated. They represent the living, breathing movement of the platform as users and items interact with and shape each other. 

### Users  

Users are the humans behind profiles that engage with the platform. And as the saying goes: if the product is free, then you are the product. Users are the ones who, by interacting with the content they care about, drive engagement and sales on the platform via advertisements. 

When a user engages with a piece of content, by definition it means that they did not quickly scroll past it and are focusing on it. This focused attention is the perfect place to show them relevant, engaging ads. The more we are able to engage users with the platform's content, the more focused they will be, and the more relevant we can make their ads, then the more likely they are to interact with said ads. 

There are pages and tomes that have been written about this overall process and whether it's good, bad, benign, etc. That's far beyond the scope of this post. This user-ad dynamic is what it is, and we move forward with the problem at hand. 

Users generally have the following stable fields from which we can extract features:
- User ID
- Networks of other Users / creators
- Historical Engagements with Items
- Categories of Interest
- Demographics
- Device

### Items

Items are the things being recommended to users. They represent the discrete choices that are shown to users, with the end goal of having users directly engage with as many of them as possible. 

In reality, users engage with a tiny fraction of the ocean of content delivered to their infinite-scroll pages and timelines. This means we don't have a balanced ML label setup and must proceed accordingly.

Items will generally have the following fields from which we can then extract features:
- Text content: the ad body, post content, video title / description, etc.
- Multimedia: images, videos, or audio tracks accompanying the item. 
- Tags / Categories: Explicit tags given by the Item's creator meant to be displayed, or the implicit subset of categories that the Item belongs to in the ecosystem. 
- Creator ID: the specific firm or creator behind this Item. 

### User-Item Engagements 

These interactions are incredibly valuable. When we don't have enough labeled data available, we can intelligently inspect and sample from a range of interaction patterns to bootstrap high-quality, meaningful datasets. 

The entities typically include the following User interactions for a specific item:
- Number of Impressions
- Likes / Dislikes
- Comments
- Shares
- Hides
- Reports

We will often need to normalize these values by thigns like: 
- The age of an Item
- The overall number of interactions
- The expected number of interactions based on the specific creator / market

This normalization gives us meaningfully scaled values that capture the range of platform behaviors. In short, we need to have a mix of historical values for these, as well as velocity and delta-based values that track how the Item is currently faring on the platform. These values must be constantly updated, and benefit from late-fusion in our chosen ML architecture.

### Behavioral Features 

These overlap in spirit with the Engagement features, but are more focused on a specific User. These are meant to capture the user's recent, dynamic behavior, and adapts to their current and evolving preferences. They include such things as:
- Device and location details
- Recent Item interactions
- Long-term, established interests across Items
- Temporal and seasonal activity 

These must also be constantly updated and benefit from late-fusion. 


The fixed entities of Users and Items benefit largely from caching. They are the reference points over which we learn cross-interactions that differentiate all kinds of platform activity. However, as mentioned, we will still need to update them and re-extract them periodically to deal with the ever-changing nature of platforms.  

The changing Engagement and Behavioral features help us capture how the platform looks *right now*, and how it is likely to evolve. They can elegantly and directly handle changing user preferences and viral platform trends. 

Both kinds of features must be carefully monitored and inspected to notice when any one of them need re-training, or when there is adversarial behavior afoot. 


## The High-Level Design  

### What we want

When it comes to recommendations, we would like to minimize both False Positives and False Negatives. Minimizing False Positives means we don't incorrectly suggest things that users are not interested in at all. Minimizing False Negatives means we don't miss recommendations that users would find truly interesting. Unfortunately in statistics and learning theory there is a fundamental tradeoff between reducing False Positives and False Negatives: there is no free lunch.

The end result is that saying we want a system with both low False Positives and low False Negatives amounts to saying "we want a really good system that doesn't make mistakes." Well, duh. Why would we want anything else? 

This inherent tradeoff makes it practically impossible to build a system that is good at both. At least for any realistic or meaningful problem space. And this is even more so the case when we factor in the scale and latency requirements of our system. 

### How we compromise 

Modern recommender systems work around this by using a multi-stage pipeline. This lets different stages focus on specific objectives such that the end result approximates that generically "good system that doesn't make mistakes." This broad architectural pattern is: 

1. Candidate Generation 
2. Lightweight Ranking
3. Heavy Re-Ranking
4. Business Re-Ranking

Step 4 is focused on business logic and heuristics, but can also exist at any point between stages 1-3. Candidates often hand-wave away this final business-focused re-ranking step. However, it is an excellent place to dovetail with the holistic, long-term business need from above that we were solving in the first place. 

Business logic and heuristics are an excellent way to make sure we are enforcing fair, diverse item recommendations that promote long-term platform health. We'll say more about this later on, but it's an easy insight to state that clearly differentiates junior vs. senior candidates. 




## Multi-Stage Recommendation Systems

### Candidate Generation 

Platforms often have hundreds of millions or billions of Items, as defined above, as part of their catalogue. It is impossible to consider every single one of them when we are making recommendations. 

Thankfully, a tremendous portion of those billion+ items are definitely not of interest to each individual customer. This means we can create a fast, lightweight candidate generation stage that grabs content we are fairly certain could be of interest to the user. 

#### Main Candidates 

The staple solution to candidate generation in modern recommender systems is the [Two Tower Approach](https://www.shaped.ai/blog/the-two-tower-model-for-recommendation-systems-a-deep-dive). This approach creates embeddings for both Users and Items. Unlike previous approaches, it directly places both embedding representations into the same latent space. It does this by having a "tower" for the User, and another for the Item, where each tower takes in its own, respective features.  

During training, Items that the User has explicitly and positively interacted with are clustered together, and Items they don't care or have actively disliked are scattered far about. 

The key insight is that, after training, the User and Item towers can operate independently. This means we can extract, store, and cache the Item embeddings for our entire catalog of offerings. If we place them in a vector store that supports fast Approximate Nearest Neighbor (ANN) such as FAISS, we can then quickly and feasibly query our entire catalog. Crucially: we can efficiently add new Items into this vector store as new Items are created by advertisers or creators. 

When we go to make a recommendation for a user, we can quickly run an ANN search with their User embedding against this live, cached, updating catalogue of Item embeddings to find the relevant items most currently relevant to them. 

#### Other Candidates 

We can also generate candidates from Collaborative Filtering approaches, which are fast enough to run at this stage and still meet our latency requirements. They were the backbone of recommender systems before the Two Tower and DeepFactorization revolutions, and can certainly still have their place in any modern, powerful pipeline. 

Lastly, we can also insert some of those aforementioned Business logic and heuristics at the candidate generation stage. We can generate candidates based on the most popular items on the platform, or from viral and growing trends, or even from large creator and advertiser campaigns. 


### Lightweight Ranking

The lightweight ranker is a small, fast model that rapidly whittles down the many candidates generated by the previous stage into a manageable subset of likely-relevant Items. 

Its main goal is to minimize False Negatives, in other words to have a high Recall. This means that it does not miss content the User will definitely be interested in. Thanks to the initial filtering of the candidate generation stage, the lightweight ranker can truly focus on making sure that it highly scores Items the user will actually be interested in.

There are two typical models for this Lightweight Ranker:  
- A tree-based model trained with XGBoost or LightGBM.
- A lightweight Neural Network that (spoiler alert) is distilled from the Heavy Re-Ranker of the following stage.

Tree-based gradient-boosted models have two incredibly attractive properties:
- They are fast enough, even on CPUs, to run well within our latency requirements.
- The nature of gradient boosting continually zeroes in and focuses its performance on False Negatives - items we should have recommended but didn't.  

The lightweight neural networks benefit from the fact that distillation is incredibly powerful. With techniques like Quantization-Aware Training and Pruning, they can also run incredibly quickly if spare GPUs are available. These distilled models are typically trained to predict the outputs to the heavy re-ranker stage.

### Heavy Re-Ranking 

Approaches like Matrix Factorization and Collaborative Filtering used to dominate recommender systems. However, like just about every field in Machine Learning, transformers have crashed onto the scene. We therefore use multi-task Sequence Transformers for the heavy re-ranking. These take the top-N outputs from the light stage, and re-score them to find the true, final order.

### Business Re-Ranking 

Lastly, we have the final re-ranking based on business logic and heuristics. This is an excellent place to enforce overall platform health, based on our holistic business objective created above. Here is where we can:
- Avoid serving too many Items from the same source
- Avoid serving too many kinds of the same Item, in a row
- Make sure we are adding Items from new, emerging creators
- Remove Items that violate any guidelines
- Remove Items that go against the user's preferences
- Avoid Items that have been flagged, or are currently under review

There could even be an emergency stop gap here, where we heavily downrank content from a known campaign by malicious, adversarial actors. 


## Features  

We spoke about this mainly in the Entities section. To recap, there are 4 broad sets of features:  

1. Fixed User demographics, with long-term preferences and behavior.
2. Fixed Item features, such as author and content at time of creation
3. User-Item interactions: the gold-mine, where we learn and see how Users are actively evolving their engagement with items.
4. Contextual / Behavioral features: how have Users recently behaved in the past? What Item were they just looking at? What time of day is it, what device are they on? How long have they been on the platform? This is the key, dynamic feature that builds off the more static bases above that determine how the user is engaging with the platform right now. 


Different features will be extracted from these. We need to process and normalize them appropriately:

- User / Item ids: categorical lookups.
- Demographics: bucketizing, and one-hot. Both for Users and Item creators
- Category preferences, for both Users and Items.
- Item content: embeddings from pre-trained models, vision, Transformer encoders, word embeddings, etc
- User / Item interactions: counts normalized by some version of age, category, expectations, bucketized, etc.
- Contextual features: rolling values of current behavior. 

## Model Training  

We will create (user, item) pairs for training where the labels are positive and negative. Positive means the Item was both relevant to the user and they enjoyed the interaction. Negative means the Item was either not relevant to the user, or they actively disliked it, or in the worst case both. 

We can either have a small set of labeled examples, or we need to create and mine the data from an intelligent processing of User-Item interactions. There is a ton to be said for each specific problem given the latter, and a senior candidate can really show their chops here. As a broad rule:
- Look at known, gold-standard Item creators and Items in the platform. How did Users interact with these? Sample across categories. These are our known, highly positive targets.
- Likewise, look at ads that *should* have done well based on similar Items, but received noticeably fewer impressions. These are weak negatives, user should have liked but didn't.
- Look at known, negative Items or even Items that came from Bot and Adversarial campaigns. How did users interact with these? These are our know, highly negative targets.
- Look at Items from smaller, emerging creators with good interactions. This rounds out the sampling from gold-standard sources to prevent popular Item over-fit. Lastly, also look at Items from smaller creators with good initial impression trajectories and outlier final impressions, minor though they may be, to learn weak positives: hidden content Users are projected to like. 

This general pattern fleshes out a good set of Strong Positive, Weak Positive, Strong Negative, and Weak Negative signals to learn from. Of course, we have to make sure we accurately sample from enough categories, and scaling becomes even more important. But it's an excellent recipe to get started. 

### Loss Functions 

Given our holistic business objective, the training loss function will be a Multi-Task objective. This lets us focus on our main "Engagement" metric, while also introducing natural regularization, adding some explainability, and letting us also make sure we train for overall platform health. 

The loose formula for this loss will be:

Loss_main = MSE/MAE for regression, or Cross-Entropy on the main engagement metric

Loss_positive_interactions = Probabilities of positive interaction (like, comment, share)

Loss_bias_correction = Weighing the loss by position to prevent over-fitting to certain locations. 

### Offline Metrics

These will be, depending on the specific task some version of:

- Precision@k
- Recall @k
- mAP
- PR-AUC
- NCDG

These will matter in different ways for different parts of the pipeline. For example, Recall@100 is the primary metric for the first stage, lightweight ranker. While Precision@20 could be the main metric for the heavyweight re-ranked.

PR-AUC generally gives a great overall view of how your system is working.

NCDG works great when there is a continuous relationship to the relevance of an item. mAP is great when there is a binary relationship between the relevance: User either engages with the Item or does not.

## Inference 

### Quantization

### Caching

### Fallbacks

## Evaluation  

### Online Metrics

### Monitoring 

## Deep Dives  

### Cold Start

### Continual Learning 

# Other writings

Hi all - here’s my comments on what to study for ML system design. Preface: my study was for E6, things may be different for your level. I also don’t know anything, these are my notes and suggestions drafted in 10 mins. These are just suggestions. And sorry I have to split this into multiple posts since I don’t have Nitro.

Alex Xu book (blue elephant one really is the bible. But it's super high level. If you do not already have a good background in ML this isn't enough to 'fake it'. Definitely read the first chapter and look into any areas you don't have too much experience in. Understand what it means to "learn embeddings"- for all possible modalities. (1/9)

I have no idea what questions get asked. People say mainly recsys, harmful content and sometimes some NLP one. Others say you always get a recsys and one other (for E6). I had 2x recsys. Chapters 6 and 7 are 100% required since recsys obviously is asked. I suggest 5 and 8 as well because this gives harmful content + a classification posed as a recsys as well (ad click prediction). You’ll likely end up reading ch 3 and 4 too since they give some basic embedding information if your’e not familiar with the content. Whilst I wasn't asked this, everyone that interviewed me worked in ads - it's likely this will come up. Don't bother looking around for "meta ML SD questions" - not helpful. Just think of a few things in your head and answer them yourself. For normal recsys, we're talking "facebook timeline", "instagram reel". For ch. 7-esque ones, we're talking about events/locations (so ephemeral recommendations/ distance based). Distance based just means you can filter results before going to your main candidate generation stage. Events means you have to take into account that cold start for items is a large factor, and once and event is over it won't get more interactions. Online learning/ dynamic feature attribution is important here (more on this later). (2/9)

For the interview itself, problem framing is incredibly important. Understand what’s being asked before continuing. Ask q’s. Give assumptions. Say what you’re hoping to improve (business) and what this translates to in ML (DAU/CTR?). Give an extremely high level model design at this stage. I won’t go into more detail here but mock interviews will help. Definitely use excalidraw. No need for shapes, just type your ideas if you can type fast. I pasted the 5 axes that you’ll be graded on into excalidraw at the beginning and filled in the details as I proceeded, so I didn’t forget what to talk about. These are (roughly) - problem framing, data pipeline, feature engineering, model design, metrics & evaluation). My interviewers were happy with me doing this (be vocal). (3/9)

For the training pipeline be aware of what your labels are, how do you get positive and negative ones? Are there things you need to account for like time travel, biases, imbalance? This is where you can hint at precision/recall-based metrics. For feature selection, I touched on it above but yes be comfortable talking about what you would use and why. Numbers: standard min-max, logarithmic. Images: ViT, CLIP, OCR. Video: VideoMoCo. Text: standard NLP techniques (n-grams, BoW, TF-IDF, lexicon matching, CBoW). ONLY when you need context encoded mention BERT. If you need to take into account cross-region (multilingual) do you talk about distillmbert (distilled multilingual BERT) and then you can hint at XLM and XLM-R. I like to use Glove for hashtags because there’s no context necessary to encode. Remember that even though BERT pre-processes, it won’t remove these. Think about mentions and URLs as well. Lexicon matching with some alignment on Levenshtein distances allows you to account for adversarial ‘attacks’ on 1337speak for example (i.e. people trying to write harmful content by evading the detectors). (4/9)

Be familiar with the different stages of the pipeline from a model perspective. For recsys you want candidate generation -> ranking. The first is high recall, second is high precision. You are working in a low latency environment and don't have the ability to process 1b+ results through an MLP. Two Tower is always a great choice for this since not only is it ‘cheap’, it allows you to learn independent representations of the “user” and “item” in the same latent space. This means on inference you just need to generate the “user” embedding, and do a simple k-NN against the pre-computed “item” embeddings to generate candidates. If you don’t know what ANN is, look it up. Be familiar with the terms FAISS, kd-trees, LSH etc. You don’t need to know them at a ridiculously low-level, just what they are and why they’re used. Do your items change a lot (event recommendations)? Sure, you can still do this, but your scoring model should have the ability to pull in “contextual”/“session” information - this is where you supplement your fixed embeddings with more data. 

Scoring/ranking is going to be some sort of MLP. Be familiar with the following models: Matrix Factorization, Neural Collaborative Filter (NCF), Neural Matrix Factorization (NeuMF), Factorization Matrix (FM), Wide & Deep, DeepFM, xDeepFM, Deep Cross Networks (DCN). Ask ChatGPT if you’re not familiar. Really understand how they each work, and when one is better than the other. In general I would go with DeepFM/DCN as my scorer, but it can depend on the application. DCN for example prioritises feature crosses (and creates them for high order polynomials). (5/9)

The main thing is - both your two tower and scorer are NNs - they can be fine tuned so suitable for continual learning. After ranking you have re-ranking. This allows you to introduce exploration, take into account policy (regional restrictions, COPPA, etc). Diversity can be introduced at this stage. Some nice add-ons for you to look into: positional bias (look into inverse propensity score), popularity bias, presentation bias. Additional pro tip: I like to say for really low latency recs that I would actually do a 3 stage system here - I would train a distilled version of the ranker model and put this earlier in the pipeline. Cheaper to run, so you can use this as an additional high-recall, medium-precision model as input to the actual ranker. 

For harmful content I don’t do a two stage model but just stick with an MLP. For this I spend more time talking about the binary classifier -> multiple binary classifier -> multi-class classifier -> multi-task classifier trade-off. Protip: in a recsys above you can generally have positive interaction data in the form of “likes”, “dwell time”, “comment”, “Report”, etc. No reason why you can’t use the chosen model for the ranker and feed it into a multi-task classification system. I did this in both of my questions. (6/9)

For evaluation & deployment give some metrics on offline and online. Offline for recsys should be some subset of precision, recall, p@k, r@k, mAP, NDCG, MRR, ROC-AUC, PR-AUC. Mention them all and then say which ones are relevant. Hint: they won’t all be. ROC-AUC is not useful for imbalanced data as much as PR-AUC may be. I.e. understand how they work, don’t just mention them. Don’t ever say accuracy. Online metrics should be linked back to the problem framing and business goals. Mention what you would monitor in production (not just latency, but DAU etc). For deployment talk about inference, this is where you can re-iterate how the embeddings in two tower are stored and cached. Talk about continual/online learning if necessary. If it is, mention catastrophic forgetting and how you’d deal with it. Discuss how you would do offline training of new models and how you’d release them (think A/B, shadow/canary deployments, rollback with a model registry etc). (7/9)

I gave tonnes of info - if most of the terms are unfamiliar you can learn it all in a week for sure. ChatGPT is your friend. Don’t believe everything. Do your own research. But more than this, do some practice. I did mock questions with ChatGPT and spent 1 hour+ on each of them. I asked for feedback. I pasted in what my recruiter gave in my initial email to hint it towards expectations. I told it “grade me as E6”, etc. Of course it’s not perfect, but I learned a lot. Ask it to ask you questions. For my interviews they didn’t seem to care about what I chose in terms of model, only that I made sensible choices for the application and could confidently answer their questions. Don’t mention things you are unfamiliar with, you’ll get caught out. I went a little further than I usually would, but I have good industry and academic experience in a lot of these areas so could think of answers on the spot for things I hadn’t played around with before. It’s a confidence game.

And finally - do a mock interview. Meetapro.com was a lot cheaper than the others (this is not an advertisement). Saying that I’ve been interviewing for 5 years+ now at FAANG so I might put my own profile up there at some point in the future. But again, a single mock should help. I did 3 to be sure. Ask them if they’d hire you. (8/9)
Now - this is all fairly specific advice, but you know yourself best. You know how much you know and what you don’t. Study where you think makes sense. My level was for E6 and this is a collection of advice I got and what worked for me. For E5 and below you may not need this much detail. For E7+ you may need more. This also isn’t an official guide or anything and definitely doesn’t cover everything, who knows what you may be asked. Might be completely different. But the knowledge within should make most questions approachable. And a big portion of it is luck at the end of the day. I have no idea what I’m doing half the time. Any other day of the week I could have failed. Just passing on knowledge that I amassed over this study period. 2 weeks ago I’d never heard of two tower and never thought about anything but MF for recsys. It’s a process. Have fun, don’t stress, good luck 🙂 .  (9/9)
(Finished - I did not read through any of this. So typos, incorrect and misleading info will surely be  in there somewhere. good luck with the grind everyone)
(and I didn't use ChatGPT :O)
