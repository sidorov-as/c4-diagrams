workspace "Payments" {
  description "Payments architecture"
  model {
    customer = person "Customer" "Pays for goods and services." {
      tags "Person,External"
      url "https://example.com/customer"
      properties {
        "segment" "retail"
      }
    }
    agent = person "Support Agent" "Investigates failed and disputed payments." {
      tags "Person,Staff"
    }
    analyst = person "Fraud Analyst" "Reviews suspicious transactions." {
      tags "Person,Staff"
    }
    payments = softwareSystem "Payments" "Collects money." {
      tags "Software System"
      web = container "Web App" "Customer checkout UI." "Django" {
        tags "Container,Frontend"
      }
      mobile = container "Mobile App" "Checkout and payment history on phones." "React Native" {
        tags "Container,Mobile"
      }
      backoffice = container "Back Office" "Payment search, refunds and disputes." "React" {
        tags "Container,Frontend"
      }
      api = container "API" "Checkout API." "FastAPI" {
        tags "Container,Critical"
        controller = component "Checkout Controller" "Validates requests and exposes the checkout endpoints." "FastAPI Router" {
          tags "Component"
        }
        checkout = component "Checkout" "Orchestrates a payment from cart to confirmation." "Python" {
          tags "Component"
        }
        risk_client = component "Risk Client" "Asks the fraud engine to score a payment." "gRPC" {
          tags "Component"
        }
        psp_adapter = component "PSP Adapter" "Talks to the payment provider and maps its errors." "Python" {
          tags "Component"
        }
        ledger_repo = component "Ledger Repository" "Persists payments and double-entry ledger records." "SQLAlchemy" {
          tags "Component"
        }
        events = component "Event Publisher" "Publishes payment lifecycle events." "Python" {
          tags "Component"
        }
      }
      fraud = container "Fraud Engine" "Scores payments in real time." "Python / scikit-learn" {
        tags "Container,Critical"
      }
      worker = container "Settlement Worker" "Settles captured payments and sends receipts." "Celery" {
        tags "Container,Worker"
      }
      broker = container "Message Broker" "Payment lifecycle events." "RabbitMQ" {
        tags "Container,Queue"
      }
      cache = container "Session Cache" "Idempotency keys and checkout sessions." "Redis" {
        tags "Container,Storage"
      }
      database = container "Database" "Payments and ledger." "PostgreSQL" {
        tags "Container,Storage"
      }
    }
    psp = softwareSystem "Payment Provider" "Card acquiring and 3-D Secure." {
      tags "Software System,External"
    }
    bank = softwareSystem "Banking Network" "Settles funds with issuing banks." {
      tags "Software System,External"
    }
    identity = softwareSystem "Identity Provider" "Authenticates customers and staff." {
      tags "Software System,External"
    }
    notifier = softwareSystem "Notification Service" "Delivers e-mail and SMS receipts." {
      tags "Software System,External"
    }
    customer -> web "Uses" "HTTPS" {
      tags "Relationship"
    }
    customer -> mobile "Uses" "HTTPS" {
      tags "Relationship"
    }
    agent -> backoffice "Looks up payments" "HTTPS" {
      tags "Relationship"
    }
    analyst -> backoffice "Reviews flagged payments" "HTTPS" {
      tags "Relationship"
    }
    web -> api "Calls" "JSON/HTTPS" {
      tags "Relationship"
    }
    mobile -> api "Calls" "JSON/HTTPS" {
      tags "Relationship"
    }
    backoffice -> api "Calls" "JSON/HTTPS" {
      tags "Relationship"
    }
    web -> identity "Signs customers in" "OIDC" {
      tags "Relationship"
    }
    backoffice -> identity "Signs staff in" "OIDC" {
      tags "Relationship"
    }
    api -> cache "Reads and writes sessions" "Redis protocol" {
      tags "Relationship"
    }
    api -> fraud "Scores payments" "gRPC" {
      tags "Relationship"
    }
    api -> psp "Authorises and captures" "HTTPS" {
      tags "Relationship,Critical"
    }
    api -> broker "Publishes events" "AMQP" {
      tags "Relationship,Async"
    }
    api -> database "Reads from and writes to" "SQL" {
      tags "Relationship,Persistent"
    }
    fraud -> database "Reads payment history" "SQL" {
      tags "Relationship"
    }
    broker -> worker "Delivers events" "AMQP" {
      tags "Relationship,Async"
    }
    worker -> database "Updates settlements" "SQL" {
      tags "Relationship,Persistent"
    }
    worker -> bank "Submits settlement files" "SFTP" {
      tags "Relationship"
    }
    worker -> notifier "Sends receipts" "HTTPS" {
      tags "Relationship,Async"
    }
    psp -> bank "Routes card transactions" "ISO 8583" {
      tags "Relationship"
    }
    web -> controller "Submits checkout" "JSON/HTTPS" {
      tags "Relationship"
    }
    mobile -> controller "Submits checkout" "JSON/HTTPS" {
      tags "Relationship"
    }
    backoffice -> controller "Requests refunds" "JSON/HTTPS" {
      tags "Relationship"
    }
    controller -> checkout "Starts payment" {
      tags "Relationship"
    }
    checkout -> risk_client "Requests risk score" {
      tags "Relationship"
    }
    checkout -> psp_adapter "Charges the card" {
      tags "Relationship"
    }
    checkout -> ledger_repo "Records payment" {
      tags "Relationship"
    }
    checkout -> events "Emits payment events" {
      tags "Relationship"
    }
    risk_client -> fraud "Scores payments" "gRPC" {
      tags "Relationship"
    }
    psp_adapter -> psp "Authorises and captures" "HTTPS" {
      tags "Relationship,Critical"
    }
    ledger_repo -> database "Reads from and writes to" "SQL" {
      tags "Relationship,Persistent"
    }
    events -> broker "Publishes events" "AMQP" {
      tags "Relationship,Async"
    }
  }
  views {
    systemLandscape "landscape" {
      include *
      autoLayout lr
    }
    systemContext payments "context" {
      include *
      exclude relationship.tag==Deprecated
      autoLayout lr
    }
    container payments "containers" {
      include *
      include element.tag==Storage
      animation {
        customer web mobile
        api cache fraud
        database broker worker
      }
      autoLayout tb
    }
    component api "components" {
      include *
      autoLayout tb
    }
    dynamic payments "checkout-flow" {
      customer -> web "Starts checkout" "HTTPS"
      web -> api "Submits checkout" "JSON/HTTPS"
      api -> fraud "Scores the payment" "gRPC"
      api -> psp "Authorises the card" "HTTPS"
      api -> database "Persists checkout" "SQL"
      api -> broker "Publishes payment captured" "AMQP"
      autoLayout lr
    }
    dynamic payments "settlement-flow" {
      broker -> worker "Delivers payment captured" "AMQP"
      worker -> database "Marks payment as settled" "SQL"
      worker -> bank "Submits settlement file" "SFTP"
      worker -> notifier "Sends receipt" "HTTPS"
      autoLayout lr
    }
    styles {
      element "Person" {
        shape Person
        background #08427b
        color #ffffff
        fontSize 22
      }
      element "Software System" {
        background #1168bd
        color #ffffff
      }
      element "Container" {
        background #438dd5
        color #ffffff
      }
      element "Component" {
        background #85bbf0
        color #000000
      }
      element "Database" {
        shape Cylinder
      }
      element "Queue" {
        shape Pipe
      }
      element "External" {
        background #999999
        color #ffffff
      }
      element "Boundary" {
        stroke #444444
        strokeWidth 1
        border Dashed
      }
      element "Person" {
        shape Person
      }
      element "Staff" {
        background #455a64
        color #ffffff
      }
      element "External" {
        background #999999
        color #ffffff
        border Dashed
      }
      element "Critical" {
        background #ffcc00
        color #111111
      }
      element "Frontend" {
        shape WebBrowser
      }
      element "Mobile" {
        shape MobileDevicePortrait
      }
      element "Storage" {
        shape Cylinder
      }
      element "Queue" {
        shape Pipe
      }
      element "Worker" {
        shape Hexagon
      }
      relationship "Persistent" {
        thickness 4
      }
      relationship "Async" {
        style dashed
      }
      relationship "Critical" {
        color #c62828
        thickness 3
      }
    }
  }
}
