#!/bin/bash

movie_data=$(python3 main.py)

# Select a movie
selected_movie=$(echo "$movie_data" | jq -r 'keys_unsorted[]' | fzf)

# Check if user pressed "q" to quit
if [ -z "$selected_movie" ]; then
    break
fi

# Display selected movie details
selected_movie_data=$(echo "$movie_data" | jq -r --arg movie_name "$selected_movie" '.[$movie_name]')
echo "$selected_movie_data" | jq --arg selected_movie "$selected_movie" 'to_entries | map({ key: .key, values: .value[]})  | .[] | "\($selected_movie) - \(.key) - \(.values.datetime) - \(.values.attributes)"' | fzf
# kaboom
