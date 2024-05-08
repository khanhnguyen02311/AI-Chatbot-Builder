import axios from "../api/axios";
import useAuth from "./useAuth";

const useRefreshToken = () => {
    const { setAuth } = useAuth();
    const refresh = async () => {
        const response = await axios.put("/auth/renew-token", {
            // put token into bearer
        });
        setAuth((prev: any) => {
            console.log(response.data.accessToken);
            return { ...prev, accessToken: response.data.accessToken };
        });
        return response.data.accessToken;
    }

    return refresh;
}

export default useRefreshToken