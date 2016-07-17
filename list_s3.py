#!/usr/bin/python
# marek.kuczynski
# @marekq
# www.marek.rocks
import boto3, time, re, datetime, json, os, sys, creds

# create timestamps
p			= '%Y-%m-%d_%H-%M'
now     		= datetime.datetime.now()
timest  		= now.strftime(p)
unixti      		= int(time.time())

# create list variables to store results
resu			= []

# check if credentials supplied as arguments or in creds.py file
def check_creds():
	global aws_access_key_id, aws_secret_access_key, region_name

	if len(sys.argv) == int(4):
		x	= sys.argv[1]
		y	= sys.argv[2]
		z	= sys.argv[3]

		if len(x) == 20 and len(y) == 40 and len(z) > int(8):
			aws_access_key_id	= x
			aws_secret_access_key	= y
			region_name		= z
			print 'valid credentials found in supplied arguments, starting...'
		else:
			exit('no valid credentials found in arguments, check again or use creds.py without arguments?')

	elif len(sys.argv) != int(1):
		exit('no valid credentials found in arguments, check again or use creds.py without arguments?')

	else:
		if len(creds.aws_access_key_id) == 20 and len(creds.aws_secret_access_key) == 40 and len(creds.region_name) > int(8):
			print 'valid credentials found in creds.py, starting'
		else:
			exit('no valid credentials found in argument or creds.py, quitting!!')
				

# retrieve metadata about all buckets
def get_s3(aws_access_key_id, aws_secret_access_key, sest, region_name):
	# authenticate with aws credentials
	session         = boto3.session.Session()
	sts_client 	= session.client('s3', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, aws_session_token = sest, region_name = region_name)

	# list buckets found in the account
	try:
		f	= sts_client.list_buckets()

	except Exception as e:
		print e
		f	= ''

	if f != '':	
		for y in f['Buckets']:
			# write the bucket policy to a json file in directory policies/
			try:
				r		= sts_client.get_bucket_policy(Bucket = y['Name'])
				f		= open('policies/bucket_'+y['Name']+'.json', 'w')
				p		= json.dumps(r, indent = 4)
				
				f.write(str(p).replace('\\', '')+'\n')
				f.close
			
			except Exception as e:
				print e 			

			# get bucket acl
			try:
				r		= sts_client.get_bucket_acl(Bucket = y['Name'])
				o		= r['Owner']['DisplayName']
				g		= r['Grants'][0]['Permission']

			except Exception as e:
				o		= ''
				g		= ''
				print e

			# get bucket metadata
			n		= y['Name']
			c		= y['CreationDate']
			l		= sts_client.get_bucket_location(Bucket=n)['LocationConstraint']
	
			# get object metadata from the bucket
			get_s3_obj(sts_client, aws_access_key_id, aws_secret_access_key, sest, l, n, c, o, g, '')

			

# get object metadata from the bucket
def get_s3_obj(sts_client, acck, seck, sest, reg, n, c, o, g, tok):
	if len(tok) > 0:
		b 		= sts_client.list_objects_v2(Bucket = n, FetchOwner = True, MaxKeys = 1000, ContinuationToken = tok)
	else:
		b 		= sts_client.list_objects_v2(Bucket = n, FetchOwner = True, MaxKeys = 1000)

	if b.has_key('Contents'):
		# capture metadata about objects in bucket
		for z in b['Contents']:
			size	= str(z['Size'])
			skey	= str(z['Key'])
			stor	= z['StorageClass']
			fmod	= z['LastModified']

			bunix	= int(time.mktime(c.timetuple()))
			funix	= int(time.mktime(fmod.timetuple()))
			
			butim	= c.strftime(p)
			fitim	= fmod.strftime(p)

			# write the results to a list
			x	= [n, skey, size, reg, o, g, stor, butim, bunix, fitim, funix]
			y	= ''

			for xx in x:
				y	+= str(xx)+','
			
			resu.append(y[:-1])
			print y[:-1]
			
	# if there is a token, retrieve additional files
	if b.has_key('NextContinuationToken'):
		tok	= b['NextContinuationToken']
		get_s3_obj(sts_client, acck, seck, sest, reg, n, c, o, g, tok)


# write the results to result.csv and timestamped file in directory s3log
def file_write():
	s3tag	= 'bucket,object-name,object-size,bucket-region,bucket-owner,bucket-permission,storage-type,bucket-create-date,bucket-create-unix,file-create-date,file-create-unix'

	f1	= open('result.csv', 'w')
	f2	= open('log/'+timest+'.csv', 'w')

	f1.write(s3tag+'\n')
	f2.write(s3tag+'\n')
	
	for x in resu:
		f1.write(x+'\n')
		f2.write(x+'\n')
	f1.close
	f2.close


# # # # #
# check credentials in creds.py and on command line arguments
check_creds()

# get s3 metadata
get_s3(creds.aws_access_key_id, creds.aws_secret_access_key, '', creds.region_name)

# write the results to logfiles
file_write()
