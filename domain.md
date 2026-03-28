```bash
export PROJECT_ID="gca-america-virtual-ta"
export REGION="us-central1"
export DOMAIN="gca-americas.dev"
```

## Reserve the Global Static IP
```bash
gcloud compute addresses create vta-lb-ip \
    --global \
    --ip-version=IPV4

# Print the IP address
gcloud compute addresses describe vta-lb-ip --global --format="value(address)"
```


## Create the Certificate Manager & DNS Auth
```bash
# 1. Create the DNS Authorization logically first natively
gcloud certificate-manager dns-authorizations create wildcard-dns-auth \
    --domain="$DOMAIN"

# 2. Get the CNAME record (MUST add this exact record to  DNS Registrar / Cloud DNS)
gcloud certificate-manager dns-authorizations describe wildcard-dns-auth

# 3. Create the Wildcard Certificate (Attaches to the auth above)
gcloud certificate-manager certificates create vta-wildcard-cert \
    --domains="*.$DOMAIN,$DOMAIN" \
    --dns-authorizations=wildcard-dns-auth

# Create a Certificate Map and attach the cert
gcloud certificate-manager maps create vta-cert-map

gcloud certificate-manager maps entries create vta-cert-map-entry \
    --map=vta-cert-map \
    --certificates=vta-wildcard-cert \
    --hostname="*.$DOMAIN"
```


## Create the Serverless Network Endpoint Group
It tells Google to look at the URL (vta1.gca-americas.dev) and route to the Cloud Run service named vta1.
```bash
gcloud compute network-endpoint-groups create vta-serverless-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-url-mask="<service>.$DOMAIN"
```

## Build the Load Balancer
Backend -> Routing Rules -> HTTPS Proxy -> Frontend
https://www.reddit.com/r/googlecloud/comments/1kwieh3/error_while_attaching_serverless_neg_backend_to/

```bash
# 1. Create the Backend Service locally first WITHOUT identifying the protocol explicitly
# (This defaults to HTTP internally and prevents the backend from forcing an empty HTTPS port)
gcloud compute backend-services create vta-backend-service \
    --global \
    --load-balancing-scheme=EXTERNAL

# 2. Attach your Native Serverless NEG (It will accepts the HTTP attachment blindly!)
gcloud compute backend-services add-backend vta-backend-service \
    --global \
    --network-endpoint-group=vta-serverless-neg \
    --network-endpoint-group-region=$REGION

# 3. Elevate the Backend Protocol formally securely to HTTPS after attachment
gcloud compute backend-services update vta-backend-service \
    --global \
    --protocol=HTTPS

# 3. Create the URL Map (Routing rules)
gcloud compute url-maps create vta-url-map \
    --default-service=vta-backend-service

# 4. Create the Target HTTPS Proxy (Attaches the Wildcard Cert Map)
gcloud compute target-https-proxies create vta-https-proxy \
    --url-map=vta-url-map \
    --certificate-map=vta-cert-map

# 5. Create the Forwarding Rule (The Frontend IP)
gcloud compute forwarding-rules create vta-lb-forwarding-rule \
    --global \
    --target-https-proxy=vta-https-proxy \
    --address=vta-lb-ip \
    --ports=443
```


Check status
```bash
gcloud certificate-manager certificates describe vta-wildcard-cert
```