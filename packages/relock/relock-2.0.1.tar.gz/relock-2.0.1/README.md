Continous Passive Authentication
================================

The Relock Session Sentinel is an automated defense software, designed for web apps dealing with the most sensitive data. It allows developers to securely implement mutual authentication with session trust assurance, streamlined and fail-proof elegant solution.

Minimal example
---------------
Run service:

    docker pull relockid/sentinel
    docker run --privileged --network host -it relock/sentinel run \
           --host 127.0.0.1 --port 8111 \
           --multiprocessing

Python:

    python3 -m pip install relock
    
    from relock import Flask as Sentinel

GitHub repository
-----------------

This repository contains ready-to-use, minimal implementation of the producer server and the consumer for test purpose of re:lock sentinel. This minimal implementation makes it easy to check how the system works in practice.

You can run the demo solution on one machine, as consumer and producer may use the same enclave for this purpose.

Links
-----

-   Docker: https://hub.docker.com/u/relockid
-   Documentation: https://relock.security/docs
-   Demo Source Code: https://github.com/relockid
-   Issue Tracker: https://github.com/relockid/sentinel/issues
-   Website: https://relock.security/