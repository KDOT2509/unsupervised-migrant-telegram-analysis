#!/bin/bash
python src/twitter_tools/search_tweets.py \
  --credential-file ~/.twitter_keys.yaml \
  --max-tweets 1000 \
  --results-per-call 100 \
  --start-time 2021-01-24 \
  --query "(#Ukraine OR #Ukrainian) (#Switzerland)" \
  --tweet-fields "created_at" \
  --filename-prefix data/twitter/switzerland/test_switzerland2 \
  --no-print-stream

