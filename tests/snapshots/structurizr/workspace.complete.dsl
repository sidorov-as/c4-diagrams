workspace "Payments" {
  description "Payments architecture"
  model {
    customer = person "Customer" {
      tags "Person,External"
      url "https://example.com/customer"
      properties {
        "segment" "retail"
      }
    }
    payments = softwareSystem "Payments" "Collects money." {
      tags "Software System"
      web = container "Web App" "Customer checkout UI." "Django" {
        tags "Container"
      }
      api = container "API" "Checkout API." "FastAPI" {
        tags "Container,Critical"
        checkout = component "Checkout" "" "Python" {
          tags "Component"
        }
      }
      database = container "Database" "" "PostgreSQL" {
        tags "Container,Storage"
      }
    }
    deploymentEnvironment "Production" {
      k8s = deploymentNode "Kubernetes" {
        tags "Boundary"
        ingress = infrastructureNode "Ingress" {
          tags "Boundary"
        }
        api_instance = containerInstance api {
          description "Checkout API."
          tags "Container,Critical"
        }
      }
    }
    customer -> web "Uses" "HTTPS" {
      tags "Relationship"
    }
    web -> api "Calls" "JSON/HTTPS" {
      tags "Relationship"
    }
    api -> database "Reads from and writes to" "SQL" {
      tags "Relationship,Persistent"
    }
  }
  views {
    systemLandscape "landscape" {
      include *
      autoLayout lr
    }
    systemContext payments "context" {
      include customer
      include payments
      exclude relationship.tag==Deprecated
      autoLayout lr
    }
    container payments "containers" {
      include *
      include element.tag==Storage
      animation {
        customer web
        api database
      }
      autoLayout tb
    }
    component api "components" {
      include *
      autoLayout lr
    }
    dynamic payments "checkout-flow" {
      customer -> web "Starts checkout" "HTTPS"
      web -> api "Submits checkout" "JSON/HTTPS"
      api -> database "Persists checkout" "SQL"
      autoLayout lr
    }
    deployment payments "Production" "production" {
      include *
      autoLayout lr
    }
    styles {
      element "Critical" {
        background #ffcc00
        color #111111
      }
      relationship "Persistent" {
        thickness 4
      }
    }
  }
}
