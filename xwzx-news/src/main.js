import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'

// 导入Vant组件库
import { 
  Button, 
  NavBar, 
  Tabbar, 
  TabbarItem, 
  Tab, 
  Tabs, 
  List, 
  PullRefresh, 
  Cell, 
  CellGroup,
  Grid,
  GridItem,
  Empty,
  Form,
  Field,
  Image,
  Toast,
  Icon,
  Popup
} from 'vant'

// 导入Vant样式
import 'vant/lib/index.css'

// 导入全局样式
import './style.css'

// 引入国际化
import { setupI18n } from './i18n'

import { useThemeStore } from './store/theme'
import { useUserStore } from './store/user'

async function bootstrap() {
  const app = createApp(App)

  const i18n = setupI18n()
  app.use(i18n)

  app.use(Button)
  app.use(NavBar)
  app.use(Tabbar)
  app.use(TabbarItem)
  app.use(Tab)
  app.use(Tabs)
  app.use(List)
  app.use(PullRefresh)
  app.use(Cell)
  app.use(CellGroup)
  app.use(Grid)
  app.use(GridItem)
  app.use(Empty)
  app.use(Form)
  app.use(Field)
  app.use(Image)
  app.use(Toast)
  app.use(Icon)
  app.use(Popup)

  app.use(router)
  app.use(pinia)

  const themeStore = useThemeStore()
  themeStore.initTheme()

  const userStore = useUserStore()
  await userStore.initializePersistedSession().catch((error) => {
    console.error('初始化持久化会话失败:', error)
  })

  app.mount('#app')
}

bootstrap()
