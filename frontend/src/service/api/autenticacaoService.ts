import axiosInstance from "../axiosInstance";
import { iLogin, iRegister } from "../../interfaces/iAutenticacao";

class AutenticacaoService {
	async login(data: iLogin) {
		const response = await axiosInstance.post("/auth", data, {
			headers: {
				"Content-Type": "application/x-www-form-urlencoded",
			},
		});
		return response;
	}

	async register(data: iRegister) {
		const response = await axiosInstance.post("/users", data, {
			headers: {
				"Content-Type": "application/json",
			},
		});
		return response;
	}
}

export default new AutenticacaoService();
