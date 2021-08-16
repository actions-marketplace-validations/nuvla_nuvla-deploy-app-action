# nuvla-deploy-app-action
A GitHub action for deploying apps from Nuvla.io into an existing infrastructure


# How to use the action (example)

This is what your workflow should look like:

```

jobs:
  test_job:
    runs-on: ubuntu-latest
    name: A job to test the action
    steps:
      - name: Tester
        id: test
        uses: nuvla/nuvla-deploy-app-action@v1
        with:
          api-key: ${{ secrets.NUVLA_USER_API_KEY }}
          api-secret: ${{ secrets.NUVLA_USER_API_KEY }}
          module-id: 'module/<uuid>'
          credential-id: 'credential/<uuid>'
          environment: 'NUVLABOX_UUID=nuvlabox/<uuid>'
      # Use the output
      - name: Get the output
        run: echo "The output was ${{ steps.test.outputs.DEPLOYMENT_ID }}"
```

# Full list of possible input parameters

```
  --api-key KEY         Nuvla.io User API Key
  --api-secret SECRET   Nuvla.io User API Secret
  --module-id MODULE_ID
                        ID of the application module to deploy
  --credential-id CREDENTIAL_ID
                        ID of the credential for the infrastructure to deploy to
  --environment ENV1=VAL1,ENV2=VAL2,...
                        (optional) Comma separated list of environment variable to define for the deployment
```

