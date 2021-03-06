# Python Project Template

[![Testing and Linting](https://github.com/guionardo/python-template/actions/workflows/python_test_and_lint.yml/badge.svg)](https://github.com/guionardo/python-template/actions/workflows/python_test_and_lint.yml)
[![CodeQL](https://github.com/guionardo/python-template/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/guionardo/python-template/actions/workflows/codeql-analysis.yml)

Add your files here

## Attention

The test and linting action will check for coverage minimum of 50%.

The COVERAGE.md file is automatically generated.

## Makefile

Ready to work

### make updatepip (install needed packages)

Make sure pipenv is installed before run this command. 

```bash
pip install --user pipenv
```

```bash
Running $ pipenv lock then $ pipenv sync.
Locking [dev-packages] dependenciesβ¦
Locking [packages] dependenciesβ¦
Updated Pipfile.lock (18d334)!
Installing dependencies from Pipfile.lock (18d334)β¦
  π   ββββββββββββββββββββββββββββββββ 23/23 β 00:00:07
```


### make test (run unit tests)

```bash
python -m unittest
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

### make coverage (run unit tests and generates COVERAGE.md)

```bash
bash .github/scripts/generate_coverage.sh
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
Wrote XML report to coverage.xml
```

### make requirements (updates requirements.txt)

```bash
pipreqs --force
INFO: Successfully saved requirements file in /home/guionardo/dev/github.com/guionardo/python-template/requirements.txt
```

## Sequence Diagram

```mermaid
sequenceDiagram
  title Wee Media Receiver Service
  autonumber
  actor front as Frontend
  participant back as API
  participant worker as Worker
  participant storage as Storage S3
  participant db as Database
  participant prc_img as Image Processor
  participant prc_vid as Video Processor

  front->>back: upload request
  alt is valid data
    activate back
    back-->>front: accepted {storage public URL}
    back->>storage: publish file 
    activate worker
    back->>worker: notify received file 
    worker->>db: insert media into database    
    worker->>worker: enqueeue notification
    deactivate worker
    deactivate back
  else no valid data
    back-->>front: rejected
  end

  loop read notifications
    note over worker: identify media type
    alt media is image
      activate prc_img
      worker->>prc_img: Process image
      note over prc_img: identify content
      note over prc_img: resize/optimize
      prc_img->>storage: update content/tagging/media_type
      prc_img->>db: update media infos and tags
      prc_img-->worker: returns
      deactivate prc_img
    else media is video
      activate prc_vid
      worker->>prc_vid: Process video
      note over prc_vid: identify content
      note over prc_vid: resize/optimize
      prc_vid->>storage: update content/tagging/media_type
      prc_vid->>db: update media infos and tags
      prc_vid-->worker: returns
      deactivate prc_vid

    end
  end
```

## PriorizaΓ§Γ£o

POST /video/{id_video}

  1. Identificar se o vΓ­deo existe no S3
  2. Existindo, retorna 202 ACCEPTED
  3. Enfileira o id_video para processamento

Processamento

  1. Download do vΓ­deo do S3
  2. AnΓ‘lise do conteΓΊdo do vΓ­deo e geraΓ§Γ£o de tags
  3. AnΓ‘lise e otimizaΓ§Γ£o do vΓ­deo
  4. Upload do novo vΓ­deo para o S3
  5. NotificaΓ§Γ£o para o site bomperfil sobre o processo terminado do vΓ­deo, com o novo nome de arquivo e as tags
  6. Com o aceite do bomperfil, exclui o arquivo anterior do S3


## GlossΓ‘rio

| NAME              | TYPE | EXAMPLE                                                                                  |
|-------------------|------|------------------------------------------------------------------------------------------|
| MEDIA_URL         | str  | https://teste-videos.us-east-1.linodeobjects.com/teste-videos/uploads/2022/06/test_2.mp4 |
| MEDIA_ID          | str  | uploads/2022/06/test.mp4                                                                 |
| POST_ID           | int  | 1234                                                                                     |
| NEW_MEDIA_ID      | str  | uploads/2022/06/test.webm                                                                |
| LOCAL_FILENAME    | str  | /tmp/filexxxx                                                                            |
| LOCAL_NEWFILENAME | str  | /tmp/fileYYYY                                                                            |
