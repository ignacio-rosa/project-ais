import zstandard
import pandas as pd
import os
import json
from datetime import datetime
import logging.handlers


log = logging.getLogger("bot")
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


def read_and_decode(reader, chunk_size, max_window_size, previous_chunk=None, bytes_read=0):
	chunk = reader.read(chunk_size)
	bytes_read += chunk_size
	if previous_chunk is not None:
		chunk = previous_chunk + chunk
	try:
		return chunk.decode()
	except UnicodeDecodeError:
		if bytes_read > max_window_size:
			raise UnicodeError(f"Unable to decode frame after reading {bytes_read:,} bytes")
		log.info(f"Decoding error with {bytes_read:,} bytes, reading another chunk")
		return read_and_decode(reader, chunk_size, max_window_size, chunk, bytes_read)


def read_lines_zst(file_name):
	with open(file_name, 'rb') as file_handle:
		buffer = ''
		reader = zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader(file_handle)
		#reader.read(40000000000)
		while True:
			chunk = read_and_decode(reader, 2**27, (2**29) * 2)

			if not chunk:
				break
			lines = (buffer + chunk).split("\n")

			for line in lines[:-1]:
				yield line, file_handle.tell()

			buffer = lines[-1]

		reader.close()

file_path = os.path.join('..', '..', 'raw_data', 'reddit_historic', 'zst') # Cambiar a método funcional
output_path = os.path.join('..', '..', 'raw_data', 'reddit_historic', 'csv') # Cambiar a método funcional
#file_path = 'home/ignacio-rosa/code/ignacio-rosa/project-ais_data/reddit/subreddits/wallstreetbets_submissions.zst'
file_lines = 0
file_bytes_processed = 0
created = None

bad_lines = 0
l_files = os.listdir(file_path)
"""l_files = ['Economics_comments.zst', 'Economics_submissions.zst',
           'economy_comments.zst', 'economy_submissions.zst',
           'finance_comments.zst', 'finance_submissions.zst',
           'business_comments.zst', 'business_submissions.zst']"""
for file in l_files:
    file_size = os.stat(file_path + '/' + file).st_size
    l_posts = []
    print(f'Analyzing {file}')
    limit = file.find('_')
    subreddit = file.replace('submissions', '').replace('comments', '').replace('.zst', '').replace('_', '')
    content_type = 'submissions' if 'submissions' in file else 'comments'
    v_ite = 0
    for line, file_bytes_processed in read_lines_zst(file_path + '/' + file):
        v_ite += 1
        try:
            obj = json.loads(line)
            created = datetime.utcfromtimestamp(int(obj['created_utc']))
            l_posts.append(obj)
        except (KeyError, json.JSONDecodeError) as err:
            bad_lines += 1
        file_lines += 1
        if file_lines % 100000 == 0:
            log.info(f"{created.strftime('%Y-%m-%d %H:%M:%S')} : {file_lines:,} : {bad_lines:,} : {file_bytes_processed:,}:{(file_bytes_processed / file_size) * 100:.0f}%")
            df = pd.DataFrame({'subreddit': [subreddit for x in range(len(l_posts))],
                       'content_type': [content_type for x in range(len(l_posts))],
                       'content': l_posts})
            df = df.to_csv(output_path + f'/{subreddit}_{content_type}_{v_ite}.csv', index=False)
            l_posts = []
            del df
    log.info(f"Complete : {file_lines:,} : {bad_lines:,}")
    df = pd.DataFrame({'subreddit': [subreddit for x in range(len(l_posts))],
                       'content_type': [content_type for x in range(len(l_posts))],
                       'content': l_posts})
    df.to_csv(output_path + f'/{subreddit}_{content_type}_{v_ite}.csv', index=False)
    del df

print(created)
print('Finished!!')
