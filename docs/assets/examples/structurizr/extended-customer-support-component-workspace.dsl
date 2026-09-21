workspace "Customer Support System - Extended Component View" {
  model {
    administrator = person "Administrator" "Internal user with administrative access." {
      tags "Person,User"
    }
    customer = person "Customer" "Owner of electronic equipment and support plan; reports issues." {
      tags "Person,User"
    }
    helpdesk = person "Helpdesk" "First line of support; provides direct phone support." {
      tags "Person,User"
    }
    manager = person "Manager" "Monitors expert performance and customer satisfaction." {
      tags "Person,User"
    }
    support_expert = person "Support Expert" "Technology expert who fixes customer electronic devices." {
      tags "Person,User"
    }
    auth0 = softwareSystem "Auth0" "External identity provider for authentication." {
      tags "Software System,External"
    }
    email_system = softwareSystem "E-mail System" "Internal mail system used for e-mail delivery." {
      tags "Software System,External"
    }
    payment_provider = softwareSystem "Payment Service Provider" "External online payment service." {
      tags "Software System,External"
    }
    sms_provider = softwareSystem "SMS Service Provider" "Provides SMS text messaging." {
      tags "Software System,External"
    }
    support = softwareSystem "Customer Support System" "Handles support tickets and expert assignments." {
      tags "Software System"
      platform = container "Support Platform" "Components that handle support tickets and expert assignments." "Container Service" {
        tags "Container"
        admin_api = component "Admin API" "User management and reference-data management." "Container Service" {
          tags "Component,Backend"
        }
        admin_portal = component "Admin Portal" "Manages system users and reference data." "Single-page Application" {
          tags "Component,Frontend"
        }
        analytics_api = component "Analytics API" "Ticket status reports, survey analysis and performance reports." "Container Service" {
          tags "Component,Backend"
        }
        api_gateway = component "API Gateway" "Performs access control, security checks and request routing." "Container Service" {
          tags "Component,Gateway"
        }
        billing_api = component "Billing API" "Billing management and financial reports." "Container Service" {
          tags "Component,Backend"
        }
        billing_portal = component "Billing Portal" "Supports billing processing." "Single-page Application" {
          tags "Component,Frontend"
        }
        customer_api = component "Customer API" "Handles registration, profiles, tickets, surveys and billing history." "Container Service" {
          tags "Component,Backend"
        }
        customer_notifications_queue = component "Customer Notifications" "Asynchronous message channel for customer notifications." "Message Queue" {
          tags "Component,Queue"
        }
        customer_portal = component "Customer Portal" "Provides access to customer profile, billing, ticket creation and history." "Single-page Application" {
          tags "Component,Frontend"
        }
        expert_notifications_queue = component "Expert Notifications" "Asynchronous message channel for expert notifications." "Message Queue" {
          tags "Component,Queue"
        }
        helpdesk_portal = component "Helpdesk Portal" "Provides access to tickets and status." "Single-page Application" {
          tags "Component,Frontend"
        }
        invoice_queue = component "Invoice" "Asynchronous message channel for invoice processing." "Message Queue" {
          tags "Component,Queue"
        }
        knowledge_base = component "Knowledge Base" "Supports searching and updating knowledge-base articles." "Single-page Application" {
          tags "Component,Frontend"
        }
        mobile_app = component "Mobile App" "Provides access to assigned tickets and knowledge-base search." "iOS / Android App" {
          tags "Component,Frontend"
        }
        notification_service = component "Notification Service" "Sends SMS and e-mail messages based on notification preferences." "Container Service" {
          tags "Component,Backend"
        }
        payment_job = component "Payment" "Runs monthly and performs payment operations." "Container Job" {
          tags "Component,Worker"
        }
        support_api = component "Support API" "Ticket orchestration, search, assignment handling and knowledge-base updates." "Container Service" {
          tags "Component,Backend"
        }
        support_dashboard = component "Support Dashboard" "Provides analytics and operational reports." "Single-page Application" {
          tags "Component,Frontend"
        }
        support_database = component "Support Database" "Stores tickets, users, customer contacts and knowledge-base content." "Relational Database" {
          tags "Component,Database"
        }
        ticket_assigned_queue = component "Ticket Assigned" "Asynchronous message channel for assigned tickets." "Message Queue" {
          tags "Component,Queue"
        }
        ticket_created_queue = component "Ticket Created" "Asynchronous message channel for created tickets." "Message Queue" {
          tags "Component,Queue"
        }
        ticket_processor = component "Ticket Processor" "Runs periodically, scans ticket statuses, and creates assignments." "Container Job" {
          tags "Component,Worker"
        }
        ticket_progress_queue = component "Ticket In-Progress/Closed" "Asynchronous message channel for ticket progress and closure notifications." "Message Queue" {
          tags "Component,Queue"
        }
      }
    }
    admin_api -> support_database "Reads from and writes to" "SQL/TCP" {
      tags "Relationship,Data"
    }
    admin_portal -> api_gateway "Makes API calls to" "REST/HTTPS" {
      tags "Relationship,Sync"
    }
    analytics_api -> support_database "Reads from and writes to" "SQL/TCP" {
      tags "Relationship,Data"
    }
    api_gateway -> customer_api "Routes API calls to" "REST/HTTP" {
      tags "Relationship,Sync"
    }
    api_gateway -> support_api "Routes API calls to" "REST/HTTP" {
      tags "Relationship,Sync"
    }
    api_gateway -> admin_api "Routes API calls to" "REST/HTTP" {
      tags "Relationship,Sync"
    }
    api_gateway -> billing_api "Routes API calls to" "REST/HTTP" {
      tags "Relationship,Sync"
    }
    api_gateway -> analytics_api "Routes API calls to" "REST/HTTP" {
      tags "Relationship,Sync"
    }
    billing_api -> support_database "Reads from and writes to" "SQL/TCP" {
      tags "Relationship,Data"
    }
    billing_portal -> api_gateway "Makes API calls to" "REST/HTTPS" {
      tags "Relationship,Sync"
    }
    customer_api -> support_database "Reads from and writes to" "SQL/TCP" {
      tags "Relationship,Data"
    }
    customer_api -> ticket_created_queue "Sends ticket created event" "Queue / Event" {
      tags "Relationship,Async"
    }
    customer_portal -> auth0 "Authenticates using" "OIDC/OAuth2" {
      tags "Relationship,External"
    }
    customer_portal -> api_gateway "Makes API calls to" "REST/HTTPS" {
      tags "Relationship,Sync"
    }
    helpdesk_portal -> api_gateway "Makes API calls to" "REST/HTTPS" {
      tags "Relationship,Sync"
    }
    knowledge_base -> api_gateway "Makes API calls to" "REST/HTTPS" {
      tags "Relationship,Sync"
    }
    mobile_app -> auth0 "Authenticates using" "OIDC/OAuth2" {
      tags "Relationship,External"
    }
    mobile_app -> api_gateway "Makes API calls to" "REST/HTTPS" {
      tags "Relationship,Sync"
    }
    notification_service -> support_database "Reads from and writes to" "SQL/TCP" {
      tags "Relationship,Data"
    }
    notification_service -> email_system "Sends e-mail using" "SMTP" {
      tags "Relationship,External"
    }
    notification_service -> sms_provider "Sends SMS using" "SMS API" {
      tags "Relationship,External"
    }
    payment_job -> support_database "Reads from and writes to" "SQL/TCP" {
      tags "Relationship,Data"
    }
    payment_job -> invoice_queue "Sends invoice event" "Queue / Event" {
      tags "Relationship,Async"
    }
    payment_job -> payment_provider "Executes payments using" "HTTPS/API" {
      tags "Relationship,External"
    }
    support_api -> support_database "Reads from and writes to" "SQL/TCP" {
      tags "Relationship,Data"
    }
    support_api -> expert_notifications_queue "Sends expert notification event" "Queue / Event" {
      tags "Relationship,Async"
    }
    support_api -> customer_notifications_queue "Sends customer notification event" "Queue / Event" {
      tags "Relationship,Async"
    }
    support_api -> ticket_progress_queue "Sends progress/closed event" "Queue / Event" {
      tags "Relationship,Async"
    }
    support_dashboard -> api_gateway "Makes API calls to" "REST/HTTPS" {
      tags "Relationship,Sync"
    }
    ticket_processor -> support_database "Reads from and writes to" "SQL/TCP" {
      tags "Relationship,Data"
    }
    ticket_processor -> ticket_assigned_queue "Sends ticket assignment event" "Queue / Event" {
      tags "Relationship,Async"
    }
    administrator -> admin_portal "Maintains users and reference data" "HTTPS" {
      tags "Relationship,Sync"
    }
    administrator -> billing_portal "Manages billing operations" "HTTPS" {
      tags "Relationship,Sync"
    }
    customer -> customer_portal "Uses" "HTTPS" {
      tags "Relationship,Sync"
    }
    customer -> mobile_app "Uses" "HTTPS" {
      tags "Relationship,Sync"
    }
    helpdesk -> helpdesk_portal "Creates/searches tickets" "HTTPS" {
      tags "Relationship,Sync"
    }
    manager -> support_dashboard "Tracks operations and generates reports" "HTTPS" {
      tags "Relationship,Sync"
    }
    support_expert -> mobile_app "Uses" "HTTPS" {
      tags "Relationship,Sync"
    }
    support_expert -> knowledge_base "Updates articles" "HTTPS" {
      tags "Relationship,Sync"
    }
    customer_notifications_queue -> notification_service "Consumed by" "Queue / Event" {
      tags "Relationship,Async"
    }
    expert_notifications_queue -> notification_service "Consumed by" "Queue / Event" {
      tags "Relationship,Async"
    }
    invoice_queue -> api_gateway "Calls billing APIs through" "REST/HTTP" {
      tags "Relationship,Async"
    }
    ticket_assigned_queue -> support_api "Consumed by" "Queue / Event" {
      tags "Relationship,Async"
    }
    ticket_created_queue -> ticket_processor "Consumed by" "Queue / Event" {
      tags "Relationship,Async"
    }
    ticket_progress_queue -> customer_api "Consumed by" "Queue / Event" {
      tags "Relationship,Async"
    }
  }
  views {
    component platform "components" {
      title "Customer Support System - Extended Component View"
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
