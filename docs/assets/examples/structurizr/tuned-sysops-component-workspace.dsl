workspace "Customer Support System - Tuned Component View" {
  model {
    customer = person "Customer" "Reports equipment issues and tracks repair progress." {
      tags "Person,User"
    }
    expert = person "Support Expert" "Accepts assignments and records repair updates." {
      tags "Person,User"
    }
    auth0 = softwareSystem "Auth0" "External identity provider." {
      tags "Software System,External"
    }
    email_system = softwareSystem "E-mail System" "Delivers customer and expert notifications." {
      tags "Software System,External"
    }
    support = softwareSystem "Customer Support System" "Handles support tickets and expert assignments." {
      tags "Software System"
      platform = container "Support Platform" "Components that handle support tickets and expert assignments." "Container Service" {
        tags "Container"
        api_gateway = component "API Gateway" "Access control and request routing." "Container Service" {
          tags "Component,Gateway"
        }
        customer_portal = component "Customer Portal" "Ticket creation and status tracking." "SPA" {
          tags "Component,Frontend"
        }
        mobile_app = component "Expert Mobile App" "Assignment queue and field repair updates." "iOS / Android" {
          tags "Component,Frontend"
        }
        notification_service = component "Notification Service" "Sends customer and expert notifications." "Container Service" {
          tags "Component,Backend"
        }
        sysops_database = component "Support Database" "Tickets, contacts, assignments, and repair history." "PostgreSQL" {
          tags "Component,Database"
        }
        ticket_api = component "Ticket API" "Ticket orchestration, search, and assignment updates." "Container Service" {
          tags "Component,Backend"
        }
        ticket_created_queue = component "Ticket Created" "Event stream for new support tickets." "Message Queue" {
          tags "Component,Queue"
        }
        ticket_processor = component "Ticket Processor" "Creates expert assignments for new tickets." "Container Job" {
          tags "Component,Worker"
        }
      }
    }
    customer -> customer_portal "Uses" "HTTPS" {
      tags "Relationship,Sync"
    }
    expert -> mobile_app "Uses" "HTTPS" {
      tags "Relationship,Sync"
    }
    customer_portal -> auth0 "Authenticates" "OIDC" {
      tags "Relationship,External"
    }
    mobile_app -> auth0 "Authenticates" "OIDC" {
      tags "Relationship,External"
    }
    customer_portal -> api_gateway "Calls" "REST/HTTPS" {
      tags "Relationship,Sync"
    }
    mobile_app -> api_gateway "Calls" "REST/HTTPS" {
      tags "Relationship,Sync"
    }
    api_gateway -> ticket_api "Routes" "REST/HTTP" {
      tags "Relationship,Sync"
    }
    ticket_api -> sysops_database "Reads/writes" "SQL/TCP" {
      tags "Relationship,Data"
    }
    ticket_processor -> sysops_database "Reads/writes" "SQL/TCP" {
      tags "Relationship,Data"
    }
    ticket_api -> ticket_created_queue "Publishes" "Queue/Event" {
      tags "Relationship,Async"
    }
    ticket_created_queue -> ticket_processor "Triggers" "Queue/Event" {
      tags "Relationship,Async"
    }
    ticket_processor -> notification_service "Requests notification" "REST/HTTP" {
      tags "Relationship,Sync"
    }
    notification_service -> email_system "Sends e-mail" "SMTP" {
      tags "Relationship,External"
    }
  }
  views {
    component platform "components" {
      title "Customer Support System - Tuned Component View"
      include *
      autoLayout tb
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
      element "User" {
        shape Person
        background #e8f5e9
        color #1b5e20
        stroke #66bb6a
      }
      element "Frontend" {
        background #e3f2fd
        color #0d47a1
        stroke #42a5f5
      }
      element "Gateway" {
        background #fce4ec
        color #880e4f
        stroke #ec407a
      }
      element "Backend" {
        background #ede7f6
        color #311b92
        stroke #7e57c2
      }
      element "Worker" {
        background #fff3e0
        color #e65100
        stroke #fb8c00
      }
      element "Database" {
        shape Cylinder
        background #fff8e1
        color #5d4037
        stroke #ffb300
      }
      element "Queue" {
        shape Pipe
        background #e0f2f1
        color #004d40
        stroke #26a69a
      }
      element "External" {
        background #f5f5f5
        color #424242
        stroke #9e9e9e
        border Dashed
      }
      relationship "Sync" {
        color #1e88e5
        thickness 2
        style solid
      }
      relationship "Data" {
        color #8d6e63
        thickness 2
        style solid
      }
      relationship "Async" {
        color #00897b
        thickness 2
        style dotted
      }
      relationship "External" {
        color #78909c
        thickness 2
        style dashed
      }
    }
  }
}
