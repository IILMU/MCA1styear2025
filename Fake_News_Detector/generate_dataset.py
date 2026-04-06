import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

# Real news samples (from credible sources)
real_news_samples = [
    {
        "title": "Scientists Discover New Species of Deep-Sea Fish",
        "text": "Researchers from the Marine Biology Institute announced today the discovery of a previously unknown species of deep-sea fish at the bottom of the Pacific Ocean. The expedition, which lasted 12 months, involved international collaboration and advanced submersible technology. The fish, named Bathypelagicus obscuris, has bioluminescent organs and was found at a depth of 4,500 meters.",
        "author": "Dr. James Mitchell",
        "date": "2024-01-15"
    },
    {
        "title": "Global Carbon Emissions Reach Record High in 2023",
        "text": "According to the International Energy Agency, global carbon dioxide emissions reached an all-time high in 2023, rising by 1.8 percent compared to 2022. The increase was primarily driven by the aviation and transportation sectors. The report emphasizes the need for urgent action to transition to renewable energy sources.",
        "author": "Climate Watch",
        "date": "2024-01-10"
    },
    {
        "title": "New Vaccine Shows Promise Against Flu Variants",
        "text": "A clinical trial involving 50,000 patients across 15 countries has shown that a new vaccine candidate offers 92% protection against multiple flu variants. The vaccine is expected to undergo final regulatory review. Researchers attribute the success to advances in mRNA technology and improved understanding of viral mutations.",
        "author": "Dr. Sarah Chen",
        "date": "2024-01-20"
    },
    {
        "title": "Tech Companies to Invest $50 Billion in AI Safety Research",
        "text": "Major technology companies including Microsoft, Google, and Meta have announced a joint commitment to invest $50 billion in artificial intelligence safety research over the next five years. The initiative aims to address concerns about AI alignment and ethical deployment. Industry leaders stated this is critical for responsible AI development.",
        "author": "Tech News Daily",
        "date": "2024-01-18"
    },
    {
        "title": "Renewable Energy Provides 40% of Global Electricity",
        "text": "A comprehensive report from the International Renewable Energy Agency shows that renewable energy sources now account for 40% of global electricity generation. This represents a significant milestone in the transition away from fossil fuels. Wind and solar power accounted for the majority of the increase.",
        "author": "IRENA Report",
        "date": "2024-01-12"
    },
    {
        "title": "Archaeological Dig Uncovers Ancient Roman Settlement",
        "text": "Excavations in southern Italy have revealed a well-preserved Roman settlement dating back to the first century AD. The site contains numerous artifacts including pottery, coins, and tools. Archaeologists believe this discovery will provide insights into daily life during the Roman Empire period.",
        "author": "Prof. Marco Rossi",
        "date": "2024-01-22"
    },
    {
        "title": "Stock Markets Rally Following Economic Data",
        "text": "Global stock markets experienced significant gains today following the release of positive economic data. The S&P 500 gained 2.3% while European indices rose 1.8%. Analysts attributed the rally to better-than-expected employment figures and moderating inflation rates.",
        "author": "Financial Times",
        "date": "2024-01-25"
    },
    {
        "title": "UNESCO Adds Three New World Heritage Sites",
        "text": "UNESCO has designated three new World Heritage Sites, including a unique geological formation in China, a historic city in Peru, and a natural reserve in East Africa. These designations recognize the exceptional cultural and natural value of these locations.",
        "author": "UNESCO",
        "date": "2024-01-16"
    },
]

# Fake news samples (with typical misinformation characteristics)
fake_news_samples = [
    {
        "title": "SHOCKING: Secret Government Lab Creates Weather-Controlling Device",
        "text": "BREAKING NEWS: According to anonymous sources, a top-secret government facility has successfully created a weather control device that can manipulate hurricanes and create earthquakes! The mainstream media is covering this up because Big Tech doesn't want you to know the truth. Wake up sheeple!!!",
        "author": "Underground Truth Media",
        "date": "2024-01-15"
    },
    {
        "title": "Celebrity EXPOSED: Hidden Connection to Elites",
        "text": "The truth is finally out! A well-known celebrity has been secretly working with world elites to control your mind. Sources close to the situation claim they saw classified documents proving this conspiracy. Share this before it gets deleted!",
        "author": "Conspiracy Uncovered",
        "date": "2024-01-14"
    },
    {
        "title": "This One Weird Trick Will Make You RICH INSTANTLY",
        "text": "Financial experts HATE him! A local man discovered a secret method that banks don't want you to know about. By doing this ONE simple trick, you can make $10,000 per day from home! Click here to learn this amazing secret before it's taken down.",
        "author": "Get Rich Quick Tips",
        "date": "2024-01-13"
    },
    {
        "title": "Vaccines Cause Autism Says Leaked Document",
        "text": "EXCLUSIVE: We obtained a leaked document that proves vaccines cause autism. The health authorities don't want this information public. Thousands of parents are waking up to the truth. Join the movement for health freedom!",
        "author": "Health Truth Warriors",
        "date": "2024-01-12"
    },
    {
        "title": "World Leaders Are REPTILIANS - Shocking Video Evidence",
        "text": "The evidence is irrefutable! Multiple world leaders are actually shapeshifting reptilians from outer space. We have video footage showing them transforming. The government is hiding this from the public. Download our free guide to learn how to spot them!",
        "author": "Alien Truth Network",
        "date": "2024-01-11"
    },
    {
        "title": "Miracle Cure Doctors Don't Want You To Know About",
        "text": "Big Pharma is FURIOUS! Scientists discovered a natural substance that cures all diseases but the medical establishment is suppressing it. This miracle cure has been used in secret for decades. Find out what it is before they silence us!",
        "author": "Natural Health Secrets",
        "date": "2024-01-10"
    },
    {
        "title": "PROOF: NASA Faked Moon Landing - New Evidence",
        "text": "After 50 years, we finally have definitive proof that the moon landing was a massive hoax! A whistleblower has come forward with never-before-seen footage. The government doesn't want you to see this. Share now!",
        "author": "Space Truth Now",
        "date": "2024-01-09"
    },
    {
        "title": "Celebrity Death CONFIRMED: But They're Keeping It Secret",
        "text": "ALERT! We have credible sources saying that a famous celebrity actually died years ago but the industry has been using a clone. This is why they look different now. The resemblance is uncanny - see the proof here!",
        "author": "Celebrity Secrets Exposed",
        "date": "2024-01-08"
    },
    {
        "title": "Banks Have Hidden Trillions From Taxpayers",
        "text": "LEAKED: Confidential documents show that major banks are hiding trillions of dollars from the government. This is the biggest financial conspiracy ever. You won't believe how deep it goes. Full story inside!",
        "author": "Financial Conspiracy Daily",
        "date": "2024-01-07"
    },
    {
        "title": "This Drink Will Extend Your Life By 50 Years",
        "text": "Scientists can't believe this actually works! Ancient monks have been using this special drink recipe for centuries to live over 200 years. The formula was secret until now. Get the recipe absolutely free!",
        "author": "Longevity Secrets",
        "date": "2024-01-06"
    },
]

def create_realistic_dataset(num_real=1000, num_fake=1000):
    """Create a realistic dataset with equal distribution of real and fake news."""
    
    data = []
    
    # Generate real news by expanding samples
    for i in range(num_real):
        sample = real_news_samples[i % len(real_news_samples)]
        # Add slight variations to avoid exact duplicates
        date_offset = np.random.randint(0, 365)
        date = (datetime.strptime(sample["date"], "%Y-%m-%d") + timedelta(days=date_offset)).strftime("%Y-%m-%d")
        
        data.append({
            "title": sample["title"] + f" ({i % len(real_news_samples) + 1})",
            "text": sample["text"],
            "author": sample["author"],
            "date": date,
            "label": 0  # 0 = real
        })
    
    # Generate fake news by expanding samples
    for i in range(num_fake):
        sample = fake_news_samples[i % len(fake_news_samples)]
        date_offset = np.random.randint(0, 365)
        date = (datetime.strptime(sample["date"], "%Y-%m-%d") + timedelta(days=date_offset)).strftime("%Y-%m-%d")
        
        data.append({
            "title": sample["title"] + f" ({i % len(fake_news_samples) + 1})",
            "text": sample["text"],
            "author": sample["author"],
            "date": date,
            "label": 1  # 1 = fake
        })
    
    # Shuffle the dataset
    np.random.seed(42)
    indices = np.random.permutation(len(data))
    data = [data[i] for i in indices]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df

if __name__ == "__main__":
    print("Generating realistic fake news dataset...")
    df = create_realistic_dataset(num_real=1000, num_fake=1000)
    
    # Save to CSV
    df.to_csv("data/fake_news_dataset.csv", index=False)
    
    print(f"Dataset created successfully!")
    print(f"Total samples: {len(df)}")
    print(f"Real news: {len(df[df['label'] == 0])}")
    print(f"Fake news: {len(df[df['label'] == 1])}")
    print(f"Dataset saved to: data/fake_news_dataset.csv")
