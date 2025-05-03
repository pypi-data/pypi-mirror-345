const {createApp, ref, onMounted} = Vue

const app = createApp({
    setup() {

  // Vue3变量创建
        const rData = ref({
            version: ""
        })

        // 配置项
        const config = ref({})

        // 通过接口刷新当前程序配置项
        function refreshConfigData() {
            pywebview.api.get_config_data().then((data) => {
                console.log("[Config]", data)
                config.value = data
            })
        }


        // 通过接口程序刷新当前页面数据
        function refreshData() {
            pywebview.api.get_data().then((data) => {
                console.log("[data]", data)
                rData.value = data
            })
        }


        // 通过接口数据将当前页面数据传递到Python
        function updateData() {
            pywebview.api.set_data(rData?.value)
        }



        const loginType = ref(1)
        let qrcodeTimmer = null



        const loginForm = ref({
            username:"",
            password:""
        })

        function login() {
            api.login(
                loginForm?.value?.username,
                loginForm?.value?.password,
            ).then((res)=>{
                api.message_error(res)
            })

        }



        function createQRCode(data) {
                const login_qrcode_element = document.getElementById('qrcode');
                if (login_qrcode_element){

                    // 生成二维码（类型、纠错等级、数据）
                    const qr = qrcode(0, 'H', location.href);
                    qr.addData(data);
                    qr.make();

                    // 渲染为 SVG 或 HTML Table

                    const svgCode = qr.createSvgTag({ cellSize: 3, margin: 4 });
                    login_qrcode_element.innerHTML = svgCode;
                }
            }



        function loginTypeChanged(t) {
            if (qrcodeTimmer){
                clearInterval(qrcodeTimmer)
            }

            if (t === 0){
                api.get_qrcode_data().then((res)=>{
                    if (res?.url){
                        createQRCode(res?.url)

                        qrcodeTimmer = setInterval(()=>{

                          api.check_qrcode_status(res?.ticket).then((loginStatus)=>{
                                if (loginStatus){
                                    clearInterval(qrcodeTimmer)
                                    api.close()
                                }

                          })

                        }, 1000)





                    }


                })

            }
        }

        return {
            rData, refreshData, updateData,
            config,refreshConfigData,


            loginType,loginForm,login,
            loginTypeChanged,
            createQRCode,
        }
    },

})
app.use(ElementPlus, {
    locale: ElementPlusLocaleZhCn
});
const vm = app.mount('#login_box')

function closeWindow() {
    pywebview.api.close()
}

async function initData() {
    const data = await pywebview.api.get_data()
    vm.rData = data ?? {}

}




// 挂载常用方法到全局变量
window.refreshData = vm.refreshData
window.refreshConfigData = vm.refreshConfigData
window.updateData = vm.updateData



// 窗口创建完毕后将调用逻辑
window.addEventListener('pywebviewready', () => {
    console.log("[INFO]桌面应用初始化成功")
    window.api = pywebview.api
    // 获取初始数据
    vm.refreshData()
    vm.refreshConfigData()
})

window.addEventListener('pywebviewready', () => {
    // 获取初始数据
    const temp_time = setInterval(()=>{

        if(!api){
            return
        }
        clearInterval(temp_time)
    }, 200)

})
