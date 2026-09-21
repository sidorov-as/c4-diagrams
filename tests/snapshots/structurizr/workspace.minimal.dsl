workspace "Workspace" {
  model {
    customer = person "Customer" {
      tags "Person"
    }
  }
  views {
    systemLandscape "landscape" {
      include *
      autoLayout lr
    }
  }
}
