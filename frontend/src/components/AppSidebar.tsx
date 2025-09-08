import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
} from "@/components/ui/sidebar"

import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { useEffect, useState } from "react";

interface UserData {
    country: string;
    display_name: string;
    followers: {
        href: string | null;
        total: number;
    };
    image_url: string; // Just the first image URL
    product: string;
}

export function AppSidebar() {
    const [loggedin, setLoggedIn] = useState(false);
    // const [token, setToken] = useState(null);
    const [songs, setSongs] = useState([]);
    const [userData, setUserData] = useState<UserData | null>(null);

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const accessToken = params.get("access_token");
        if (accessToken) {
            // setToken(accessToken);
            setLoggedIn(true);
            window.history.replaceState({}, document.title, "/");
            // fetchLikedSongs(accessToken);
            fetchUserData(accessToken);
        }
    }, []);

    function login() {
        // just redirect to backend /login
        window.location.href = "http://localhost:3000/login";
    }

    async function fetchLikedSongs(token: any) {
        try {
            const res = await fetch("http://localhost:3000/get-liked-songs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ accessToken: token })
            })

            const data = await res.json();
            setSongs(data);
            // console.log('songs data:', data);

        } catch (error) {
            console.log(error)
        }
    }

    async function fetchUserData(token: any) {
        try {
            const res = await fetch("http://localhost:3000/get-userData", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ accessToken: token })
            })
            const res_data = await res.json();

            const data: UserData = {
                country: res_data.country,
                display_name: res_data.display_name,
                followers: res_data.followers,
                image_url: res_data.images[0]?.url || '',
                product: res_data.product,
            }
            setUserData(data)

        } catch (error) {
            console.log("error: ", error)
        }
    }
    return (
        <Sidebar side="left" variant="floating" >
            <SidebarHeader>
                <p>Sortify</p>
            </SidebarHeader>
            <SidebarContent>
                <SidebarGroup>
                    <SidebarGroupLabel></SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {!loggedin ? (
                                <Button onClick={login}>
                                    Connect Spotify
                                </Button>
                            ) : (
                                <div>
                                    <p>Connected to Spotify</p>
                                    <p>{songs.length} liked songs</p>
                                    <p>{userData?.followers.total} followers</p>
                                </div>
                            )}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>
            <SidebarFooter>
                <div>
                    {
                        userData ?
                            <div>
                                <Avatar>
                                    <AvatarImage src={userData.image_url} />
                                    <AvatarFallback>CN</AvatarFallback>
                                </Avatar>
                                <p>{userData.display_name}</p>
                            </div>
                            :
                            <Avatar>
                                <AvatarFallback>PK</AvatarFallback>
                            </Avatar>
                    }
                </div>
            </SidebarFooter>
        </Sidebar>
    )
}