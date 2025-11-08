import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarProvider,
} from "@/components/ui/sidebar"

import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { useEffect, useState } from "react"
import StickerPeel from "./StickerPeel"

interface UserData {
  country: string
  display_name: string
  email: string
  followers: {
    href: string | null
    total: number
  }
  image_url: string
  product: string
}

export function AppSidebar() {
  const [loggedin, setLoggedIn] = useState(false)
  const [songs, setSongs] = useState([])
  const [userData, setUserData] = useState<UserData | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const accessToken = params.get("access_token")

    if (accessToken) {
      setLoggedIn(true)
      window.history.replaceState({}, document.title, "/")
      fetchUserData(accessToken)
    }
  }, [])

  function login() {
    window.location.href = "http://localhost:3000/login"
  }

  async function fetchUserData(token: any) {
    try {
      const res = await fetch("http://localhost:3000/get-userData", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accessToken: token }),
      })
      const res_data = await res.json()

      const data: UserData = {
        country: res_data.country,
        display_name: res_data.display_name,
        email: res_data.email,
        followers: res_data.followers,
        image_url: res_data.images[0]?.url || "",
        product: res_data.product,
      }
      setUserData(data)
    } catch (error) {
      console.log("error: ", error)
    }
  }

  return (
    <SidebarProvider>
      <div className="h-full">
        <Sidebar side="left" variant="floating">
          <SidebarHeader className="prose">
            <h1>SingedIn</h1>
          </SidebarHeader>

          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel />
              <SidebarGroupContent>
                <SidebarMenu>
                  {!loggedin ? (
                    <Button onClick={login} className="prose">
                      Connect Spotify
                    </Button>
                  ) : (
                    <div className="prose">
                      <p>Connected to Spotify</p>
                      <p>{songs.length} liked songs</p>
                      <p>{userData?.followers.total} followers</p>
                      <div className="bg-red-400">
                        <StickerPeel
                          imageSrc={
                            "https://i.scdn.co/image/ab67616d0000b27385ff52b3a1e03d96c915531e"
                          }
                          width={50}
                          rotate={20}
                          peelBackHoverPct={20}
                          peelBackActivePct={10}
                          shadowIntensity={0.1}
                          lightingIntensity={0.1}
                        />
                      </div>
                    </div>
                  )}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>

          <SidebarFooter>
            <div>
              {userData ? (
                <div>
                  <Avatar>
                    <AvatarImage src={userData.image_url} />
                    <AvatarFallback>CN</AvatarFallback>
                  </Avatar>
                  <p>{userData.display_name}</p>
                  <p>{userData.email}</p>
                </div>
              ) : (
                <Avatar>
                  <AvatarFallback>PK</AvatarFallback>
                </Avatar>
              )}
            </div>
          </SidebarFooter>
        </Sidebar>
      </div>
    </SidebarProvider>
  )
}
