workspace "Workspace" {
  model {
    customer = person "Customer" {
      tags "Person"
    }
    shop = softwareSystem "Online Shop" {
      tags "Software System"
    }
    customer -> shop "Buys goods" {
      tags "Relationship"
    }
  }
  views {
    systemLandscape "landscape" {
      include *
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
    }
  }
}
