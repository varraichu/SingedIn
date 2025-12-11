import { MicVocal, User } from 'lucide-react';
import { Button } from "@/components/ui/button"
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "@/components/ui/navigation-menu"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { useEffect, useState } from 'react';

const navigationLinks = [
  { href: "/", label: "Chat", active: true },
  // { href: "about", label: "About", active: false },
]

interface User {
  avatar: string
  email: string
  followers: number
  profile: string
  username: string
}

export default function NavBar() {

  const [loggedIn, setLoggedIn] = useState(false)
  const [userData, setUserData] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)



  useEffect(() => {
    checkAuthStatus()
  }, [])


  useEffect(() => {
    if (loggedIn && !userData) {
      // fetchUserData()
    }
  }, [loggedIn])

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/get_user_data', {
        credentials: 'include'
      })
      if (response.ok) {
        const result = await response.json()
        console.log("User data: ", result)
        setUserData(result as User)
        setLoggedIn(true)
      } else {
        setLoggedIn(false)
        setUserData(null)
      }
    } catch (error) {
      console.log("Auth check error: ", error)
      setLoggedIn(false)
      setUserData(null)
    } finally {
      setLoading(false)
    }
  }

  const fetchUserData = async () => {
    const url = 'http://127.0.0.1:8000/api/get_user_data'
    try {
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`Response Status: ${response.status}`)
      }
      const result = await response.json()
      console.log("User data: ", result)
      setUserData(result)
    }
    catch (error) {
      console.log("Fetching user data error: ", error)
    }
  }

  const handleLogin = () => {
    window.location.href = "http://127.0.0.1:8000/api/login"
  }

  const handleUserDataClick = async () => {
    if (userData) {
      console.log("Current user data:", userData)
      alert(JSON.stringify(userData, null, 2))
    }
    else{
      setLoading(true);
      try{
        const data = await fetchUserData();
        console.log("heheh")
      }
      catch(error){

      }
    }
  }

  return (
    <header className="border-b px-4 md:px-6">
      <div className="flex h-12 items-center justify-between gap-4">
        {/* Left side */}
        <div className="flex items-center gap-2">
          {/* Mobile menu trigger */}
          <Popover>
            <PopoverTrigger asChild>
              <Button
                className="group size-8 md:hidden"
                variant="ghost"
                size="icon"
              >
                <svg
                  className="pointer-events-none"
                  width={16}
                  height={16}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M4 12L20 12"
                    className="origin-center -translate-y-[7px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.1)] group-aria-expanded:translate-x-0 group-aria-expanded:translate-y-0 group-aria-expanded:rotate-[315deg]"
                  />
                  <path
                    d="M4 12H20"
                    className="origin-center transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.8)] group-aria-expanded:rotate-45"
                  />
                  <path
                    d="M4 12H20"
                    className="origin-center translate-y-[7px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.1)] group-aria-expanded:translate-y-0 group-aria-expanded:rotate-[135deg]"
                  />
                </svg>
              </Button>
            </PopoverTrigger>
            <PopoverContent align="start" className="w-36 p-1 md:hidden">
              <NavigationMenu className="max-w-none *:w-full">
                <NavigationMenuList className="flex-col items-start gap-0 md:gap-2">
                  {navigationLinks.map((link, index) => (
                    <NavigationMenuItem key={index} className="w-full">
                      <NavigationMenuLink
                        href={link.href}
                        className="py-1.5"
                        active={link.active}
                      >
                        {link.label}
                      </NavigationMenuLink>
                    </NavigationMenuItem>
                  ))}
                </NavigationMenuList>
              </NavigationMenu>
            </PopoverContent>
          </Popover>
          {/* Main nav */}
          <div className="flex items-center gap-6">
            <div className="text-primary">
              <MicVocal />
            </div>
            {/* Navigation menu */}
            {/* <NavigationMenu className="max-md:hidden">
              <NavigationMenuList className="gap-2">
                {navigationLinks.map((link, index) => (
                  <NavigationMenuItem key={index}>
                    <NavigationMenuLink
                      active={link.active}
                      href={link.href}
                      className="text-muted-foreground hover:text-primary py-1.5 font-medium"
                    >
                      {link.label}
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                ))}
              </NavigationMenuList>
            </NavigationMenu> */}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button asChild variant="ghost" size="sm" className="text-sm">
            <a href="https://www.linkedin.com/in/qasim-anwar/" target="_blank">Show love</a>
          </Button>
          <Button
            size="sm"
            className="text-sm"
            onClick={loggedIn ? handleUserDataClick : handleLogin}
            disabled={loading}
          >
            {loading ? "Loading..." : (loggedIn && !userData) ? "Fetch Data" : (loggedIn && userData)? userData?.username : "Connect Spotify"}
          </Button>
        </div>
      </div>
    </header>
  )
}