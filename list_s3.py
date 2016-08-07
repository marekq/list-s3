#!/usr/bin/python
# marek kuczynski
# @marekq
# www.marek.rocks

# configure the bucketname to write result CSV file to

bucketn	= 'lists3marek'	

# AWS bucket API key and bucket name to write the CSV file with results to - if you leave these blank, the lambda service role will be used which is prefered
s3acck = ''
s3seck = ''
s3_region_name = 'eu-west-1'

# AWS account to list the S3 buckets and files in them for - if you leave these blank, the lambda service role will be used which is prefered

aws_acck = ''
aws_seck = ''
aws_region_name = 'eu-west-1'


########## ! # ! # don't touch anything below this line # ! # ! ##########

import boto3, time, re, datetime, json, os, sys

# create timestamp format for strftime
timest	= '%Y-%m-%d_%H-%M'

# retrieve metadata about all buckets
def get_s3(aws_acck, aws_seck, aws_sest, aws_region_name):
	global resu
	resu = []
	
	session = boto3.session.Session()

	if len(aws_seck) == 0 and len(aws_acck) == 0:
		sts_client = session.client('s3', region_name = aws_region_name)
		
	else:
		sts_client = session.client('s3', region_name = aws_region_name, aws_access_key_id = aws_acck, aws_secret_access_key = aws_seck, aws_session_token = '')
		
		f = sts_client.list_buckets()
		
		if f != '':
			for y in f['Buckets']:
				try:
					r    	= sts_client.get_bucket_acl(Bucket = y['Name'])
					owne 	= r['Owner']['DisplayName']
					gran 	= r['Grants'][0]['Permission']
					
				except Exception as e:
					owne	= ''
					grant	= ''
					print e

					name	= y['Name']
					crea	= y['CreationDate']
					loca	= sts_client.get_bucket_location(Bucket = name)['LocationConstraint']
					
					get_s3_obj(sts_client, name, crea, owne, gran, '')
					# get_s3_web(sts_client, name)


# get object metadata from the bucket
def get_s3_obj(sts_client, name, crea, owne, gran, tok):
	if len(tok) > 0:
		b = sts_client.list_objects_v2(Bucket = name, FetchOwner = True, MaxKeys = 1000, ContinuationToken = tok)
	else:
		b = sts_client.list_objects_v2(Bucket = name, FetchOwner = True, MaxKeys = 1000)

	# capture metadata about objects in bucket
	if b.has_key('Contents'):
		for z in b['Contents']:
			size	= str(z['Size'])
			skey	= str(z['Key'])
			stor	= z['StorageClass']
			fmod	= z['LastModified']

			bunix	= int(time.mktime(crea.timetuple()))
			funix	= int(time.mktime(fmod.timetuple()))
			butim	= crea.strftime(timest)
			fitim	= fmod.strftime(timest)
			reg     = ''
			
			# write the results to a list
			x       = [name, skey, size, reg, owne, gran, stor, butim, bunix, fitim, funix]
			y   	= ''
			
			for xx in x:
				y += str(xx)+','
				
				resu.append(y[:-1])
				print 'RUN: '+y[:-1]


	# if there is a token, retrieve additional files by calling the script again
	if b.has_key('NextContinuationToken'):
		tok	= b['NextContinuationToken']
		get_s3_obj(sts_client, name, crea, owne, gran, tok)


# get s3 website attached to a bucket
def get_s3_web(sts_client, bucket):
	try:
		s3web = sts_client.get_bucket_website(Bucket = bucket)
		print str(s3web)

	except Exception as e:
		print e


# write the results to result.csv and timestamped file in directory s3log
def file_write():
	s3tag	= 'bucket,object-name,object-size,bucket-region,bucket-owner,'
	s3tag   += 'bucket-permission,storage-type,bucket-create-date,'
	s3tag   += 'bucket-create-unix,file-create-date,file-create-unix'
	
	now     = datetime.datetime.now()
	timest  = now.strftime()
	filen   = 'lambda-'+str(timest)+'.csv'  
	
	f1	    = open('/tmp/lambda-'+str(timest)+'.csv', 'w')
	f1.write(s3tag+'\n')
	for x in resu:
		f1.write(x+'\n')
		f1.close
		
		put_s3(bucketn, filen)


def put_s3(bucketn, filen):
	session     = boto3.session.Session()
	if len(s3acck) == 0 and len(s3seck) == 0:
		sts_client  = session.client('s3', region_name = s3_region_name)    
	else:
		sts_client  = session.client('s3', region_name = s3_region_name, aws_access_key_id = s3acck, aws_secret_access_key = s3seck)
			
	sts_client.upload_file('/tmp/'+filen, bucketn, filen)
				
				
# kick off the lambda function

def lambda_handler(event, context):
	get_s3(aws_acck, aws_seck, '', aws_region_name)
	file_write()
