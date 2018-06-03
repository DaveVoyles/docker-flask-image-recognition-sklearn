
# Docker container running a flask web server for image classification using Scikit-Learn

#### Author(s): The team at TD Bank | Dave Voyles, MSFT | [@DaveVoyles](http://www.twitter.com/DaveVoyles)
#### URL: [www.DaveVoyles.com](http://www.davevoyles.com)

Create a docker container and host it in Azure with this tutorial
----------
### Why would you want to use this?
Imagine that you have built a machine learning model and want others to be able to use it. You'd have to host it somewhere, and as more users hit the endpoint with the model, you'll need to scale dynamically to assure they have a fast and consistent experience. This project includes a number of simple, yet helpful tools.

**Docker**

Docker is a platform that allows users to easily pack, distribute, and manage applications within containers. It's an open-source project that automates the deployment of applications inside software containers. Gone are the days of an IT professional saying  "*Well, it worked on my machine.*" Not it works on all of our machines.

**Flask**

Flask is great for developers working on small projects that need a quick way to make a simple, Python-powered web site. It powers loads of small one-off tools, or simple web interfaces built over existing APIs.

**Scikit-Learn**

Scikit-Learn is a simple and efficient tools for data mining and data analysis, which is built on NumPy, SciPy, and matplotlib. It does a lot of the dirty work involved with machine learning, and allows you to quickly build models, make predicitons, and manage your data.

Once your docker container is deployed, you simply make an HTTP Post request to ```<YourWebsite>:5000/classify``` with the URL of an image in the body, and the model will return a label for what it think best describes is in the image. At the moment it is trained to detect:
-    axes
-    boots
-    carabiners
-    crampons
-    gloves
-    hardshell jackets
-    harnesses
-    helmets
-    insulated jackets
-    pulleys
-    rope
-    tents

### Is this re-usable? Can I use my own trained model?
Yes!

You could easily train it to classify other objects, too. All of the code for this project is contained in the app.py file, and the trained model is contained in the pickle_model.pkl file.

Simply replace the *pickle_model.pkl* file with a trained model of your own.

*App.py* contains the code which does several things:

- Resizes the image 
- Normalizes the image
- Parses the JSON POST request you made to its endpoint
- Calls the trained model
- Returns the classification result

The trained model, contained in *pickle_model.pkl* expects all images to be resized (128x128) and normalized, so if you're creating a new model of your own, you may want to keep this bit of code. 

### Buld the image & run it locally
In a terminal, navigate to the folder containing the .dockerfile.
This will create a new docker image and tag it with the name of your repository, name of the image, and the version
It will take a few minutes to download & install all of the required files
```
docker build -t davevoyles/flask-sklearn-classification:latest . 
```

Run the image locally in debug mode and expose ports 5000
```
docker run -d --name flask-sklearn-classification -p 5000:5000 davevoyles/flask-sklearn-classification
```


### Verify everything works locally, then remove the image
``` docker ps ```


``` docker logs flask-sklearn-classification ```


``` docker rm -f docker logs flask-sklearn-classification ```


Push to docker hub account name/repository. This may take a few minutes
```
docker push davevoyles/flask-sklearn-classification
```

### Login to Azure via CLI
```
az login 
```

### Create resource group (one time)
```
az group create -l eastus -n dv-containers-rg
```

### Create a container in Azure
Create a container in azure w/ a public IP so that we can make HTTP post requests and expose port 5000.
Pull image from dockerhub *account/repository/tag*
```
az container create --resource-group dv-containers-rg --name dv-flask-container --image davevoyles/flask-sklearn-classification:latest --ip-address public --location eastus --ports 5000
```

Check status of container by querying the ip address. You may have to wait a few minutes for it to complete.
```
az container show --resource-group dv-containers-rg --name dv-flask-container --query ipAddress
```

It should return with something like this:

```json
{
  "additionalProperties": {},
  "dnsNameLabel": null,
  "fqdn": null,
  "ip": "40.114.107.193",
  "ports": [
    {
      "additionalProperties": {},
      "port": 5000,
      "protocol": "TCP"
    }
  ]
}
```

### View the logs for your container      

``` 
az container logs --resource-group dv-containers-rg --name dv-flask-container
```


You can also log into the Azure portal in your browser to see if your container service is running.

![Azure Portal 1](/Images/az-portal-1.png)

![Azure Portal 2](/Images/az-portal-2.png)



## Example requests
Swap the IP address listed below with your own. These will return the label of the image you passed in. For example:

```json 
{"classification": "insulated_jackets"}
```

```json
curl -X POST \
  http://40.117.156.248:5000/classify \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
"url":"https://images.thenorthface.com/is/image/TheNorthFace/NF0A2VD5_KX7_hero?$638x745$"
}'
```

```json
curl -X POST \
  http://40.121.22.230:5000/classify \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
"url":"https://images.thenorthface.com/is/image/TheNorthFace/NF0A2VD5_KX7_hero?$638x745$"
}'
```

```json
curl -X POST \
  http://40.121.22.230:5000/classify \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
"url":"https://m.fortnine.ca/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/catalogimages/gmax/gm45-half-helmet-matte-black-xs.jpg"
}'
```

```json
curl -X POST \
  http://40.121.22.230:5000/classify \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
"url":"https://images.sportsdirect.com/images/products/90800440_l.jpg"
}'
```

```json
curl -X POST \
  http://40.121.22.230:5000/classify \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
"url":"https://mec.imgix.net/medias/sys_master/high-res/high-res/8860680618014/5052314-SIL00.jpg?w=600&h=600&auto=format&q=60&fit=fill&bg=FFF"
}'
```


### Delete the container

```
az container delete --name dv-flask-container --resource-group dv-containers-rgt
```
